using System.Collections;
using System.Collections.Generic;
using UnityEngine;

using System.Runtime.InteropServices;


// Optimizerクラス
// OptimizerオブジェクトにAttachされている
public class Optimizer : MonoBehaviour
{
    // DLL関数定義：最適化開始
    [DllImport("__Internal")]
    private static extern void OptimizerStart();

    // DLL関数定義：評価値通知
    [DllImport("__Internal")]
    private static extern void OptimizerStep(float score);

    // DLL関数定義：最適化終了
    [DllImport("__Internal")]
    private static extern void OptimizerEnd();

    // Start is called before the first frame update
    void Start()
    {
        // 最適化開始
        OptimizerStart();
    }

    // Update is called once per frame
    void Update()
    {

    }

    // パラメータ通知（DLLから呼ばれる）
    void OnParam(string str)
    {
        // CSVをパラメータに分解
        string[] arr =  str.Split(',');
        float x1 = float.Parse(arr[0]);
        float x2 = float.Parse(arr[1]);
        Debug.Log("OnParam called");
        Debug.LogFormat("x1={0}, x2={1}", x1, x2);
        // Booth Function
        float score = Mathf.Pow((x1 + 2*x2 - 7),2) + Mathf.Pow((2*x1 + x2 - 5),2);
        // 評価値通知
        OptimizerStep(score);
    }

    // ベストパラメータ通知（DLLから呼ばれる）
    void OnBestParam(string str)
    {
        // CSVをベストパラメータに分解
        string[] arr =  str.Split(',');
        float x1 = float.Parse(arr[0]);
        float x2 = float.Parse(arr[1]);
        Debug.Log("OnBestParam called");
        Debug.LogFormat("x1={0}, x2={1}", x1, x2);
        // 最適化終了
        OptimizerEnd();
    }

    // エラー通知（DLLから呼ばれる）
    void OnError(string str)
    {
        Debug.Log("OnError called");
        // エラー理由or箇所
        Debug.LogFormat("str = {0}", str);
        // 最適化終了
        OptimizerEnd();
    }
}
