
# Unity～Ax連携サンプルプログラム

Unity（WebGL）とAxを連携させるサンプルプログラムです。

* 動作環境
* インストール
* 実行手順
* ブログ

### 動作環境

筆者の動作環境とソフトウェアのバージョンです。

```
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
```

### インストール

* Python仮想環境の構築と、ライブラリのインストール手順です。
* PyTorchのコマンドラインは動作環境によって異なります。  
詳細はPyTorch公式を参照してください。
https://pytorch.org/get-started/locally/

Python仮想環境

```sh
conda create -n ax-sample python=3.7
conda activate ax-sample
```

Pythonライブラリ

```sh
conda install pytorch torchvision cpuonly -c pytorch
pip install ax-platform Flask gevent gevent-websocket
```

### 実行手順

1. サーバーアプリ起動  
`python app.py`
1. ブラウザからURLにアクセス  
`http://localhost:8080`
    * URLにアクセスするとすぐ最適化処理がスタートします。
    * Unityの画面には何も表示されません。
    * 適宜ブラウザおよびサーバーのコンソールでログを確認してください。

#### ブログ

本リポジトリの内容は下記ブログと連動しています。  
詳細はこちらをご参照ください。  
https://tech.morikatron.ai/
