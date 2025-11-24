void setup() {
  Serial.begin(115200);
}

const int fsize = 30; // Filter size for each channel
int bufferA0[fsize], bufferA1[fsize], bufferA2[fsize]; // Buffers for each analog pin
int indexA0 = 0, indexA1 = 0, indexA2 = 0; // Indices for each buffer

void loop() {
  // Read analog values from each pin
  int valueA0 = analogRead(A0);
  int valueA1 = analogRead(A1);
  int valueA2 = analogRead(A2);

  // Update buffers
  bufferA0[indexA0] = valueA0;
  bufferA1[indexA1] = valueA1;
  bufferA2[indexA2] = valueA2;

  // Update indices
  indexA0 = (indexA0 + 1) % fsize;
  indexA1 = (indexA1 + 1) % fsize;
  indexA2 = (indexA2 + 1) % fsize;

  // Calculate averages
  float avgA0 = calculateAverage(bufferA0);
  float avgA1 = calculateAverage(bufferA1);
  float avgA2 = calculateAverage(bufferA2);

  // Print formatted output for the Serial Plotter
  Serial.print(valueA0);
  Serial.print(",");
  Serial.print(avgA0);
  Serial.print(",");
  Serial.print(valueA1);
  Serial.print(",");
  Serial.print(avgA1);
  Serial.print(",");
  Serial.print(valueA2);
  Serial.print(",");
  Serial.println(avgA2);

  delay(10);  // Small delay to stabilize readings
}

// Function to calculate the moving average of the given buffer
float calculateAverage(int buffer[]) {
  float sum = 0.0;
  for (int i = 0; i < fsize; i++) {
    sum += buffer[i];
  }
  return sum / fsize;
}
