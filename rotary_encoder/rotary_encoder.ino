#include <MsTimer2.h> //タイマーライブラリの読み込み
#include <Encoder.h> //ロータリーエンコーダライブラリの読み込み
 
Encoder myEnc(9, 8); //ロータリーエンコーダ信号に使うピンを9,10に設定
volatile long oldPosition  = -999; //割り込み処理で使う変数はvolatileにすると安心
volatile long newPosition  = 0;

void RotEnc() { //割り込み処理の関数
                //ライブラリで得たロータリーエンコーダの数値をキープするだけ
  newPosition = myEnc.read();
}

void setup() {
  Serial.begin(9600);
  //割り込み処理の設定
  MsTimer2::set(1, RotEnc); //1ms(ミリ秒)で設定
  MsTimer2::start();
}
 
void loop() {
  //ロータリーエンコーダの数値が変化した時だけシリアルに出力
  if (newPosition != oldPosition) {
    oldPosition = newPosition;
    Serial.println(newPosition);
  }
}