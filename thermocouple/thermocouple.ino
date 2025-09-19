//Lesson 70 熱電対を用いた温度センサモジュール(MAX6675)
//MAX6675 ICが実装されたモジュールを使用して熱電対で温度を測定
//https://omoroya.com/

//SPI通信用の予約語 SS(10),MOSI(11),MISO(12),SCK(13)
#include <SPI.h>
int value; // MAX6675からのデータ格納変数

void setup() {
  //SPI通信の初期設定
  SPI.setBitOrder(MSBFIRST);           // 上位ビットから送信
  SPI.setClockDivider(SPI_CLOCK_DIV4); // 分周期1/4指定 16MHz/4=4MHz(MAX6675仕様：Max 4.3MHz)
  SPI.setDataMode(SPI_MODE0);          // アイドル時Low、立上がりエッジでデータ取得
  SPI.begin();                         // SPI通信の初期化、有効化
  Serial.begin(9600);                  // シリアル通信のデータ転送レートを9600bpsで指定
}

void loop() { 
  
  //温度データ読み出し
  delay(500);                       // MAX6675仕様(Conversion Time > 220ms)
  digitalWrite(SS, LOW);            // 制御デバイス選択(Enable)
  value = SPI.transfer(0x00) << 8;  // 上位ビット8bit読み出し後8bit左にシフト
  value |= SPI.transfer(0x00);      // 下位ビット8bit読み出し後上位ビットとOR
  digitalWrite(SS, HIGH);           // 制御デバイス選択(Disable)

  //熱電対のopen check(bit<2> = 1ならopen)
  if ((value & 0x0004) != 0){
    Serial.println("Open Error");
    
  //読み出した温度の表示 bit<14:3>が温度数値格納bit bit<15>=0(dummy bit)
  } else {
    //Serial.print((value >> 3), BIN); //bit<15:3>のみ2進表示
    //Serial.print(", ");
    Serial.print((value >> 3) * 0.25); //bit<15:3>のみ表示、MAX6675仕様(分解能 0.25℃)
    Serial.println(" degC");
  } 
  
}