import json

from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

from flask import Flask, request, render_template, Blueprint

from booth_loop import Optimizer

# Unity WebGLのテンプレートのフォルダ構成に合わせるため
# Blueprintを利用してstatic_folderを追加する
app = Flask(__name__, static_folder="TemplateData")
app.config.from_object(__name__)
blueprint = Blueprint('optimizer', __name__, static_folder='Build',
                      template_folder=".")
app.register_blueprint(blueprint)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/optimizer')
def optimizer():
    if request.environ.get('wsgi.websocket'):
        # WebSocket接続
        ws = request.environ['wsgi.websocket']
        # パラメータ通知コールバック
        def cb_step(x):
            # メッセージ作成：パラメータ通知
            data = {'m': 'OPTIMIZER_PARAM', 'x': x.tolist()}
            print(data)
            # WebSocektメッセージ送信
            ws.send(json.dumps(data))
            print('Waiting...')
            # WebSocketメッセージ待ち受け
            message = ws.receive()
            score = 0
            if message:
                print(message)
                data2 = json.loads(message)
                score = data2['score']
            return score

        # ベストパラメータ通知コールバック
        def cb_end(x):
            # メッセージ作成：ベストパラメータ通知
            data = {'m': 'OPTIMIZER_BEST_PARAM', 'x': x.tolist()}
            print(data)
            # WebSocektメッセージ送信
            ws.send(json.dumps(data))
            print('Waiting...')
            # WebSocketメッセージ待ち受け
            message = ws.receive()
            if message:
                print(message)

        obj = Optimizer(cb_step, cb_end)
        obj.optimize()
        ws.close()
    return "OK"


if __name__ == '__main__':
    app.debug = True

    host = 'localhost'
    port = 8080

    host_port = (host, port)
    server = WSGIServer(
        host_port,
        app,
        handler_class=WebSocketHandler
    )
    server.serve_forever()
