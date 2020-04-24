// 外部スクリプト
// ビルドでコンパイルされない＝ビルドなしで編集可能
var OptimizerExt = {

    // 最適化開始
    OptimizerStart: function (callback) {
        console.log('OptimizerStart');
        // URL作成
        //var host = "ws://localhost:8080/optimizer";
        var protocol = location.protocol == 'https:' ? 'wss:' : 'ws:';
        var host = protocol + "//" + location.host + location.pathname + "/optimizer";
        console.log(host);
        try {
            // WebSocket接続
            this.g_ws = new WebSocket(host);
        }
        catch (e) {
            window.alert(e);
            console.error(e);
            callback('Optimizer', 'OnError', 'OptimizerStart');
        }
        this.g_ws.onmessage = function (message) {
            // WebSocket受信ハンドラ
            var message_data = JSON.parse(message.data);
            var m = message_data['m'];
            var x = message_data['x'];
            var str = '';
            for (var i = 0; i < x.length; i++) {
                if (i == 0) {
                    str += x[i];
                } else {
                    str += ',' + x[i];
                }
            }
            if (m == 'OPTIMIZER_PARAM') {
                // パラメータ通知
                callback('Optimizer', 'OnParam', str);
            } else if (m == 'OPTIMIZER_BEST_PARAM') {
                // ベストパラメータ通知
                callback('Optimizer', 'OnBestParam', str);
            } else {
                callback('Optimizer', 'OnError', 'OptimizerStart');
            }
        };
    },

    // 評価値通知
    OptimizerStep: function (score, callback) {
        console.log('OptimizerStep');
        // メッセージ作成：評価値通知
        var data = { 'score': score, 'm': 'OPTIMIZER_STEP' };
        var message = JSON.stringify(data);
        try {
            // WebSocketメッセージ送信
            this.g_ws.send(message);
        }
        catch (e) {
            window.alert(e);
            console.error(e);
            callback('Optimizer', 'OnError', 'OptimizerStep');
        }
    },

    // 最適化終了
    OptimizerEnd: function (callback) {
        console.log('OptimizerEnd');
        // メッセージ作成：最適化終了
        var data = { 'm': 'OPTIMIZER_END' };
        var message = JSON.stringify(data);
        try {
            // WebSocketメッセージ送信
            this.g_ws.send(message);
        }
        catch (e) {
            window.alert(e);
            console.error(e);
            callback('Optimizer', 'OnError', 'OptimizerStep');
        }
        this.g_ws.onclose = function (event) {
            // WebSocket切断ハンドラ
            console.log(event);
            console.log('Disconnected');
        };
        try {
            // WebSocket切断
            this.g_ws.close()
        }
        catch (e) {
            window.alert(e);
            console.error(e);
            callback('Optimizer', 'OnError', 'OptimizerEnd');
        }
    },
}
