// ==========================================
// Robot Control (Arm & Omnidirectional wheels)全能機器人整合控制 (手臂 + 全向輪)
// ==========================================

// --- Arm ---
int ARM_IN1 = 22;
int ARM_IN2 = 24; // Claw Motor
int ARM_IN3 = 26;
int ARM_IN4 = 28; // Stretching Motor

// --- Omnidirectional Wheels ---
// Front&Left 左前 (FL)
int FL_IN1 = 11; int FL_IN2 = 10;
// Behind&Left左後 (BL)
int BL_IN1 = 9; int BL_IN2 = 8;
// Front&Right右前 (FR)
int FR_IN1 = 47; int FR_IN2 = 49;
// Behind&Right右後 (BR)
int BR_IN1 = 51; int BR_IN2 = 53;

void setup() {
  Serial.begin(9600); // Baud Rate setting 開啟通訊

  // 1. Arm  Pin Setting初始化手臂腳位
  pinMode(ARM_IN1, OUTPUT); pinMode(ARM_IN2, OUTPUT);
  pinMode(ARM_IN3, OUTPUT); pinMode(ARM_IN4, OUTPUT);

  // 2. Wheel Pins Settings初始化輪子腳位
  pinMode(FL_IN1, OUTPUT); pinMode(FL_IN2, OUTPUT);
  pinMode(FR_IN1, OUTPUT); pinMode(FR_IN2, OUTPUT);
  pinMode(BL_IN1, OUTPUT); pinMode(BL_IN2, OUTPUT);
  pinMode(BR_IN1, OUTPUT); pinMode(BR_IN2, OUTPUT);

  stop_all(); // Stop initially 預設全部停止
  Serial.println("Robot Ready: Arm + Wheels");
}

void loop() {
  // Python Command 監聽 Python 指令
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    switch (cmd) {
      // --- Arm Control手臂控制區 ---
      case '1': // Stretch Arm 伸長
        digitalWrite(ARM_IN1, LOW); digitalWrite(ARM_IN2, HIGH);
        break;
      case '2': // Arm Contraction 縮回
        digitalWrite(ARM_IN1, HIGH); digitalWrite(ARM_IN2, LOW);
        break;
      case '3': // Grabbing 夾取
        digitalWrite(ARM_IN3, HIGH); digitalWrite(ARM_IN4, LOW);
        break;
      case '4': // Put Down 放開
        digitalWrite(ARM_IN3, LOW); digitalWrite(ARM_IN4, HIGH);
        break;

      // --- Wheel Control 輪子控制區 ---
      case 'F': moveForward(); break;
      case 'B': moveBackward(); break;
      case 'L': moveLeft(); break;
      case 'R': moveRight(); break;
      case 'Q': rotateLeft(); break;
      case 'E': rotateRight(); break;

      // --- Stop 停止區 ---
      case 'S': // 停止所有 (輪子+手臂)
      case 's': 
        stop_all();
        break;
    }
  }
}

// =======================
// Actions 動作函式庫
// =======================

void stop_all() {
  // Stop the Arm 停手臂
  digitalWrite(ARM_IN1, LOW); digitalWrite(ARM_IN2, LOW);
  digitalWrite(ARM_IN3, LOW); digitalWrite(ARM_IN4, LOW);
  // Stop the Wheel 停輪子
  motor(1, 0); motor(2, 0); motor(3, 0); motor(4, 0);
}

// --- Wheel Movement Definition輪子動作定義 ---
void moveForward() { motor(1, 1); motor(2, 1); motor(3, 1); motor(4, 1); }
void moveBackward(){ motor(1, -1); motor(2, -1); motor(3, -1); motor(4, -1); }
void moveLeft()    { motor(1, -1); motor(2, 1); motor(3, 1); motor(4, -1); } 
void moveRight()   { motor(1, 1); motor(2, -1); motor(3, -1); motor(4, 1); } 
void rotateLeft()  { motor(1, -1); motor(2, 1); motor(3, -1); motor(4, 1); }
void rotateRight() { motor(1, 1); motor(2, -1); motor(3, 1); motor(4, -1); }

// --- Wheel Motor Commands底層馬達驅動 (查表法) ---
void motor(int id, int dir) {
  int in1, in2;
  if (id == 1)      { in1 = FL_IN1; in2 = FL_IN2; }
  else if (id == 2) { in1 = FR_IN1; in2 = FR_IN2; }
  else if (id == 3) { in1 = BL_IN1; in2 = BL_IN2; }
  else if (id == 4) { in1 = BR_IN1; in2 = BR_IN2; }
  else return;

  if (dir == 1)      { digitalWrite(in1, HIGH); digitalWrite(in2, LOW); }
  else if (dir == -1){ digitalWrite(in1, LOW); digitalWrite(in2, HIGH); }
  else               { digitalWrite(in1, LOW); digitalWrite(in2, LOW); }
}