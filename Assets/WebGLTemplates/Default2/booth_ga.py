import random

import numpy as np

from deap import base
from deap import creator
from deap import tools

# パラメータ定義テーブル（Ax仕様）
PARAMETERS = [
    {
        "name": "x1",
        "type": "range",
        "bounds": [-10.0, 10.0],
        "value_type": "float",
    },
    {
        "name": "x2",
        "type": "range",
        "bounds": [-10.0, 10.0],
        "value_type": "float",
    },
]

LOCUS = np.array([128, 64, 32, 16, 8, 4, 2, 1])  # 数値変換テーブル
NLOCUS = len(LOCUS)  # 数値変換テーブルのビット数
NPARAM = len(PARAMETERS)  # パラメータ数
NBIT = NLOCUS*NPARAM  # ビット数

NGEN = 40  # 世代数
NPOP = 300  # 集団の個体数
CXPB = 0.5  # 交叉率
MUTPB = 0.2  # 突然変異率（個体）
INDPB = 0.05  # 突然変異率（ビット）

DEF_SELECT_NUM = 0  # 選択個体数（0:全個体、0<:選択個体数指定）


# Optimizerクラス
class Optimizer():
    def __init__(self, cb_step=None, cb_end=None, select_num=DEF_SELECT_NUM):
        self.cb_step = cb_step  # ステップ・コールバック
        self.cb_end = cb_end  # 終了コールバック
        if select_num > NPOP or select_num < 0:
            raise ValueError("out of range: select_num", select_num)
        self.select_num = select_num  # 選択個体数（0の場合は全個体）

        # 最小化
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        # 遺伝子タイプ
        # Attribute generator
        #                      define 'attr_bool' to be an attribute ('gene')
        #                      which corresponds to integers sampled uniformly
        #                      from the range [0,1] (i.e. 0 or 1 with equal
        #                      probability)
        toolbox.register("attr_bool", random.randint, 0, 1)  # ビット

        # 初期化
        # Structure initializers
        #                         define 'individual' to be an individual
        #                         consisting of 100 'attr_bool' elements ('genes')
        # 個体
        toolbox.register("individual", tools.initRepeat, creator.Individual,
            toolbox.attr_bool, NBIT)

        # 集団
        # define the population to be a list of individuals
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # 評価関数
        # ----------
        # Operator registration
        # ----------
        # register the goal / fitness function
        toolbox.register("evaluate", self.evaluate)

        # 交叉
        # register the crossover operator
        toolbox.register("mate", tools.cxTwoPoint)  # 2点交叉

        # 突然変異
        # register a mutation operator with a probability to
        # flip each attribute/gene of 0.05
        toolbox.register("mutate", tools.mutFlipBit, indpb=INDPB)  # ビットフリップ

        # 個体選択
        # operator for selecting individuals for breeding the next
        # generation: each individual of the current generation
        # is replaced by the 'fittest' (best) of three individuals
        # drawn randomly from the current generation.
        toolbox.register("select", tools.selTournament, tournsize=3)  # トーナメント
        # toolbox.register("select", tools.selRoulette)  # ルーレット
        # toolbox.register("select", tools.selBest)  # ランキング

        self.toolbox = toolbox

    # 数値変換
    def b2n(self, l):
        # l: 1パラメータ分のビット列
        return sum(l*LOCUS)

    # レンジ変換
    def scale(self, a, fromBound, toBound, t):
        # a: 変換元数値
        # fromBound, toBount: 変換前後のレンジ
        # t: キャスト型
        (min1, max1) = fromBound
        (min2, max2) = toBound
        ret = a/(max1-min1)*(max2-min2)+min2
        ret = t(ret)
        ret = max(min2, ret)
        ret = min(max2, ret)
        return ret

    # 遺伝子to実数リスト変換
    def getX(self, individual):
        # individual: 1個体分のビット列

        # 最適化対象パラメータの値を配列にセットする
        ls = np.array(individual).reshape([NPARAM, NLOCUS])
        ret = []
        for i, l in enumerate(ls):
            # Ax仕様のパラメータ定義テーブル
            p = PARAMETERS[i]

            type = p['type']
            if type == 'range':
                # タイプ＝レンジの場合
                bounds = p['bounds']  # レンジ
                value_type = p['value_type']  # 型

                # 型変換
                t = eval(value_type)
                xmin = t(bounds[0])
                xmax = t(bounds[1])

                # 実数・レンジ変換
                x = self.scale(self.b2n(l), (0, sum(LOCUS)), (xmin, xmax), t)

            elif type == 'choice':
                # タイプ＝択一の場合
                values = p['values']  # 選択肢
                bounds = [values[0], values[-1]]  # レンジ
                value_type = p['value_type']  # 型

                # 型変換
                t = eval(value_type)
                xmin = t(bounds[0])
                xmax = t(bounds[1])

                # 実数・レンジ変換
                x = self.scale(self.b2n(l), (0, sum(LOCUS)), (xmin, xmax), t)

                # 選択肢に振り分け
                n = len(values)
                for j in range(n):
                    a = xmin + (xmax - xmin)/n * j
                    b = xmin + (xmax - xmin)/n * (j+1)
                    if x >= a and x < b:
                        x = values[j]
                        break

            elif type == 'fixed':
                # タイプ＝固定の場合
                value = p['value']  # 固定値
                x = value

            else:
                raise ValueError("unknown parameter type", type)

            ret.append(x)
        return np.array(ret)

    # count = 0

    # 評価関数
    def evaluate(self, individual):
        # self.count += 1
        # print(self.count)

        # 最適化対象パラメータの値を配列にセットする
        x = self.getX(individual)
        if self.cb_step:
            # パラメータ通知コールバック
            # クライアントへ今回のパラメータを通知し、評価値の受信を待ち受ける
            score = self.cb_step(x)
        else:
            # スクリプト単体で動作させる場合
            x1 = x[0]
            x2 = x[1]
            # Booth Function
            score = (x1 + 2*x2 - 7)**2 + (2*x1 + x2 - 5)**2
        return score,

    # 最適化関数
    def optimize(self, ngen=NGEN):
        # random.seed(64)

        # create an initial population of 300 individuals (where
        # each individual is a list of integers)
        pop = self.toolbox.population(n=NPOP)

        # エリート保存個体
        hof = tools.HallOfFame(1)

        # CXPB  is the probability with which two individuals
        #       are crossed
        #
        # MUTPB is the probability for mutating an individual
        # CXPB, MUTPB = 0.5, 0.2

        print("Start of evolution")

        # Evaluate the entire population
        fitnesses = list(map(self.toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit

        # エリート個体の更新
        hof.update(pop)

        print("  Evaluated %i individuals" % len(pop))

        # Extracting all the fitnesses of
        fits = [ind.fitness.values[0] for ind in pop]

        # Variable keeping track of the number of generations
        g = 0

        # Begin the evolution
        while g < ngen:
            # A new generation
            g = g + 1
            print("-- Generation %i --" % g)

            # Select the next generation individuals
            if self.select_num:
                # 選択個体数指定の場合
                offspring = self.toolbox.select(pop, self.select_num)
            else:
                offspring = self.toolbox.select(pop, len(pop))

            # Clone the selected individuals
            offspring = list(map(self.toolbox.clone, offspring))

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring[::2], offspring[1::2]):

                # cross two individuals with probability CXPB
                if random.random() < CXPB:
                    self.toolbox.mate(child1, child2)

                    # fitness values of the children
                    # must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:

                # mutate an individual with probability MUTPB
                if random.random() < MUTPB:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            print("  Evaluated %i individuals" % len(invalid_ind))

            # The population is entirely replaced by the offspring
            if self.select_num:
                # 選択個体数指定の場合
                pop.extend(offspring)
                rmv = tools.selWorst(pop, self.select_num)
                for r in rmv:
                    pop.remove(r)
                # print("len(pop)", len(pop))
                # print("len(offspring)", len(offspring))
            else:
                pop[:] = offspring

            # エリート個体の更新
            hof.update(pop)

            # Gather all the fitnesses in one list and print the stats
            fits = [ind.fitness.values[0] for ind in pop]

            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5

            print("  Min %s" % min(fits))
            print("  Max %s" % max(fits))
            print("  Avg %s" % mean)
            print("  Std %s" % std)

        print("-- End of (successful) evolution --")

        # ベストパラメータ＝最適解に最も近づいた値
        # best_ind = tools.selBest(pop, 1)[0]
        best_ind = hof.items[0]
        print("Best individual is %s, %s" % (best_ind, best_ind.fitness.values))
        best_parameters = self.getX(best_ind)
        print(best_parameters)

        if self.cb_end:
            # 終了コールバック：Unityアプリへベストパラメータを通知する
            self.cb_end(best_parameters)


if __name__ == "__main__":
    obj = Optimizer(select_num=DEF_SELECT_2K)
    obj.optimize()
