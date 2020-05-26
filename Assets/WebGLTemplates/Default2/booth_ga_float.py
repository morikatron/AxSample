import array
import random

import numpy as np

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

NBIT = 2  # パラメータ数

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
        # creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)

        toolbox = base.Toolbox()

        # 遺伝子タイプ
        # Attribute generator
        toolbox.register("attr_float", random.uniform, -10, 10)  # 実数値GA

        # 初期化
        # Structure initializers
        # 個体
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, NBIT)
        # 集団
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # レンジチェック
        def checkBounds(min, max):
            def decorator(func):
                def wrappper(*args, **kargs):
                    offspring = func(*args, **kargs)
                    for child in offspring:
                        for i in range(len(child)):
                            if child[i] > max:
                                child[i] = max
                            elif child[i] < min:
                                child[i] = min
                    return offspring
                return wrappper
            return decorator

        # 評価関数
        toolbox.register("evaluate", self.evaluate)
        # 交叉
        toolbox.register("mate", tools.cxBlend, alpha=1.5)
        # 突然変異
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=3, indpb=INDPB)
        # 個体選択
        toolbox.register("select", tools.selTournament, tournsize=3)  # トーナメント
        # toolbox.register("select", tools.selRoulette)  # ルーレット
        # toolbox.register("select", tools.selBest)  # ランキング

        # レンジチェック
        toolbox.decorate("mate", checkBounds(-10, 10))
        toolbox.decorate("mutate", checkBounds(-10, 10))

        self.toolbox = toolbox


    # 遺伝子to実数リスト変換
    def getX(self, individual):
        return np.array(individual)

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

        LAMBDA = 100
        pop = self.toolbox.population(n=NPOP)
        # エリート保存個体
        hof = tools.ParetoFront()
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean, axis=0)
        stats.register("std", np.std, axis=0)
        stats.register("min", np.min, axis=0)
        stats.register("max", np.max, axis=0)

        algorithms.eaMuPlusLambda(pop, self.toolbox, mu=NPOP, lambda_=LAMBDA,
                                  cxpb=CXPB, mutpb=MUTPB, ngen=ngen,
                                  stats=stats, halloffame=hof)

        # ベストパラメータ＝最適解に最も近づいた値
        best_ind = hof.items[0]
        print(best_ind)
        print(best_ind.fitness.values)
        best_parameters = self.getX(best_ind)
        print(best_parameters)

        if self.cb_end:
            # 終了コールバック：Unityアプリへベストパラメータを通知する
            self.cb_end(best_parameters)

        # return pop, stats, hof


if __name__ == "__main__":
    obj = Optimizer()
    obj.optimize()
