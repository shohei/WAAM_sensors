// Arduino側のサンプル
int sensor1 = A0;
int sensor2 = A1;

void setup() {
  Serial.begin(9600); // Raspberry Pi側と同じボーレートにする
}

void loop() {
  int val1 = analogRead(sensor1);
  int val2 = analogRead(sensor2);

  // カンマ区切りで送信（例: "512,678\n"）
  Serial.print(val1);
  Serial.print(",");
  Serial.println(val2);

  delay(500); // 0.5秒ごとに送信
}