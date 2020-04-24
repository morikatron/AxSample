// DLLスクリプト
// ビルドでコンパイルされる
mergeInto(LibraryManager.library, {

  // 最適化開始
  OptimizerStart: function () {
    // 外部スクリプトの対応関数をコール
    OptimizerExt.OptimizerStart(function (oname, fname, param) {
      // Unityスクリプトの関数をコール
      SendMessage(oname, fname, param);
    });
  },

  // 評価値通知
  OptimizerStep: function (score) {
    // 外部スクリプトの対応関数をコール
    OptimizerExt.OptimizerStep(score, function (oname, fname, param) {
      // Unityスクリプトの関数をコール
      SendMessage(oname, fname, param);
    });
  },

  // 最適化終了
  OptimizerEnd: function () {
    // 外部スクリプトの対応関数をコール
    OptimizerExt.OptimizerEnd(function (oname, fname, param) {
      // Unityスクリプトの関数をコール
      SendMessage(oname, fname, param);
    });
  },

});
