import numpy as np
from ax import optimize


# Optimizerクラス
class Optimizer:
    def __init__(self, cb_step=None, cb_end=None):
        self.cb_step = cb_step  # ステップ・コールバック
        self.cb_end = cb_end  # 終了コールバック

    # 評価関数
    def evaluation_function(self, parameterization):
        l = len(parameterization)
        # 最適化対象パラメータの値を配列にセットする
        x = np.array([parameterization.get(f"x{i+1}") for i in range(l)])
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
        return {"score": (score, 0.0)}

    # 最適化関数
    def optimize(self):
        # ax.optimizeをコールする
        # ax.optimizeは最適化が終了するまで復帰して来ない
        # ax.optimize内でevaluation_functionが試行回数分コールされる
        best_parameters, best_values, experiment, model = optimize(
            parameters=[  # 最適化対象パラメータの定義
                {
                "name": "x1",
                "type": "range",
                "bounds": [-10.0, 10.0],
                },
                {
                "name": "x2",
                "type": "range",
                "bounds": [-10.0, 10.0],
                },
            ],
            # 評価関数（オリジナルコード）
            # evaluation_function=lambda p: (p["x1"] + 2*p["x2"] - 7)**2 + (2*p["x1"] + p["x2"] - 5)**2,
            evaluation_function=self.evaluation_function,  # 評価関数
            objective_name="score",  # 評価指標の名前
            minimize=True,  # 最適化＝最小化
        )
        # best_parameters contains {'x1': 1.02, 'x2': 2.97};
        # the global min is (1, 3)
        # ベストパラメータ＝最適解に最も近づいた値
        print(f"best_parameters = {best_parameters}")

        # その他指標
        means, covariances = best_values
        print(f"means = {means}")

        if self.cb_end:
            # 終了コールバック：Unityアプリへベストパラメータを通知する
            x1 = best_parameters['x1']
            x2 = best_parameters['x2']
            x = np.array([x1, x2])
            self.cb_end(x)


if __name__ == '__main__':
    obj = Optimizer()
    obj.optimize()
