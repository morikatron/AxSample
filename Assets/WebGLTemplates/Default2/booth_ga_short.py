import array
import random

import numpy as np

from deap import algorithms
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


# Optimizerクラス
class Optimizer():
    def __init__(self, cb_step=None, cb_end=None):
        self.cb_step = cb_step  # ステップ・コールバック
        self.cb_end = cb_end  # 終了コールバック

        # 最小化
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        # 遺伝子タイプ
        # Attribute generator
        toolbox.register("attr_bool", random.randint, 0, 1)  # ビット

        # 初期化
        # Structure initializers
        # 個体
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, NBIT)
        # 集団
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # 評価関数
        toolbox.register("evaluate", self.evaluate)
        # 交叉
        toolbox.register("mate", tools.cxTwoPoint)  # 2点交叉
        # 突然変異
        toolbox.register("mutate", tools.mutFlipBit, indpb=INDPB)  # フリップビット
        # 個体選択
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
        score = 0
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

        
        pop = self.toolbox.population(n=NPOP)
        # エリート保存個体
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        pop, log = algorithms.eaSimple(pop, self.toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=ngen,
                                       stats=stats, halloffame=hof, verbose=True)

        # ベストパラメータ＝最適解に最も近づいた値
        best_ind = hof.items[0]
        print(best_ind)
        print(best_ind.fitness.values)
        best_parameters = self.getX(best_ind)
        print(best_parameters)

        if self.cb_end:
            # 終了コールバック：Unityアプリへベストパラメータを通知する
            self.cb_end(best_parameters)

        # return pop, log, hof


if __name__ == "__main__":
    obj = Optimizer()
    obj.optimize()
