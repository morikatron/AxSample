
# Unity～Ax連携サンプルプログラム

Unity（WebGL）とAx（Adaptive Experimentation Platform）を連携させるサンプルプログラムです。

* ブログ
* 動作環境
* Unity WebGLビルド
* Pythonライブラリ
* 実行手順
* 遺伝的アルゴリズム【追記】

### ブログ

本リポジトリの内容はブログと連動しています。  
詳細はこちらをご参照ください。  
https://tech.morikatron.ai/entry/2020/05/06/100000

【追記】  
遺伝的アルゴリズムのサンプルコードを追加しました。  
詳しくは下記ブログ記事を参照してください。  
（GA追加に関するブログエントリは6月8日公開予定です）  
https://tech.morikatron.ai/entry/2020/06/08/100000

### 動作環境

筆者の動作環境とソフトウェアのバージョンです。

* Windows 10 Pro 1909
* Google Chrome 81.0.4044.113
* Unity 2019.3.1f1
* Miniconda3（conda 4.8.3）
* python 3.7.7
* torch 1.5.0
* torchvision 0.6.0
* ax-platform 0.1.11
* Flask 1.1.2
* gevent 20.4.0
* gevent-websocket 0.10.1
* deap 1.3.1【追記】

### Unity WebGLビルド

1. git clone [URL]
1. Unity EditorでAxSampleプロジェクトを開く
1. Assets/Scenes/SampleSceneを選択
1. File>Build Settings...を開く
    * Scenes In Build>Add Open Scenesを実行
    * Platform>WebGL>Switch Platformを実行
    * Player Settings...>Player>WebGL Settings>Resolution and Presentation>WebGL Template>Default2を選択
    * Buildを実行
        * ビルド先フォルダとして新しいフォルダWebGLを作成し選択
1. ビルドエラーがなければOK

### Pythonライブラリ

* 一部前述の[インストール]と重複します。
* PyTorchのインストールコマンドは動作環境によって異なります。  
詳細はPyTorch公式を参照してください。  
https://pytorch.org/get-started/locally/

仮想環境  
`conda create -n ax-sample python=3.7` 

`conda activate ax-sample`

PyTorch  
`conda install pytorch torchvision cpuonly -c pytorch` 

Ax他  
`pip install ax-platform Flask gevent gevent-websocket`  
または  
`cd AxSample; pip install -r requirements.txt`

DEAP【追記】
`pip install deap`

### 実行手順

1. 仮想環境を起動  
`conda activate ax-sample`
1. WebGLビルド先のフォルダに移動  
`cd AxSample/WebGL`
1. サーバーアプリ起動  
`python app.py`
1. ブラウザからURLにアクセス  
`http://localhost:8080/` または `http://127.0.01:8080/`
    * URLにアクセスするとすぐ最適化処理がスタートします。
    * Unityの画面には何も表示されません。
    * 適宜ブラウザおよびサーバーのコンソールでログを確認してください。

### 遺伝的アルゴリズム【追記】

適宜app.pyにてOptimizerを切り替えてください。

【app.py 抜粋】
```python
from booth_loop import Optimizer  # ベイズ最適化
# from booth_ga_short import Optimizer  # シンプルGA（簡易版）
# from booth_ga import Optimizer  # シンプルGA（フルスペック版）
# from booth_ga_float import Optimizer  # 実数値GA
```
