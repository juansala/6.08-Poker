#include "Arduino.h"
#include "Poker.h"

Poker::Poker(char* user_id, TFT_eSPI tft){
  sprintf(USER_ID,user_id);
  sprintf(host, "608dev-2.net");
  initialized = 0; //whether user's been initialized in game
  sprintf(GAME_STATE, "DEAL"); //initialize to DEAL to generate
  sprintf(PREV_STATE, "DEAL");
  hand_index = 0;
  bet_added = 0;
  tft_g = tft;
  result = 0;
  timer = millis();
}

int Poker::update(int button1, int button2){
  if (strcmp(GAME_STATE, "DEAL") == 0 && !initialized){
    makeGame();
    getGame(); //update GAME_STATE and other info
    initialized = 1;
  }
  if (millis()-5000 > timer){ //Get game info every 5 sec
    getGame();
    timer = millis();
    Serial.println("TEST");
    if (strcmp(GAME_STATE, "DEAL") == 0){
      tft_g.drawString("Waiting for other player...", 0, 0, 1);
    }
  }
  if (button2 == 2){ //button2 long press -> fold detected
    requestPOST("fold", "NULL", "NULL");
  }
  if (strcmp(GAME_STATE, PREV_STATE) != 0){
    tft_g.fillScreen(TFT_BLACK);
    sprintf(PREV_STATE, GAME_STATE);
  }
  if (strcmp(GAME_STATE, "BET_1") == 0){
    displayCards(false);
    if (strcmp(CURRENT_PLAYER, USER_ID) == 0){
      tft_g.drawString("Add Bet: ", 0, 60, 1);
      tft_g.drawString("         ", 0, 100, 1); //clear the "not your turn" message
      if (button1 == 1){ //button1 short press -> add to bet only on screen
        bet_added = bet_added + 1;
        char tempStr[10];
        sprintf(tempStr, "%d", bet_added);
        tft_g.drawString(tempStr, 60, 60, 1);
      }
      if (button2 == 1){ //button2 short press -> finish turn, POST bet
        char tempStr[10];
        sprintf(tempStr, "%d", bet_added); 
        requestPOST("bet", tempStr, "NULL");
        bet_added = 0;
      }
    }
    else {
      tft_g.drawString("Not your turn.", 0, 100, 1);
    }
  }
  if (strcmp(GAME_STATE, "DISCARD") == 0){
    //Serial.println("It's discarding time!");
    displayCards(false);
    if (strcmp(CURRENT_PLAYER, USER_ID) == 0){
      tft_g.drawString("Discard: ", 0, 60, 1);
      tft_g.drawString("         ", 0, 100, 1); //clear the "not your turn" message
      if (button1 == 1){ //button1 short press -> browse through cards
        hand_index++;
        sprintf(chosen_card, "%s,", hand_array[((hand_index % 5) + 5) % 5]);
        tft_g.drawString(chosen_card, 60, 60, 1);
      }
      if (button1 == 2){ //button1 long press -> select card to discard
        strcat(discarded, chosen_card);
        tft_g.drawString("Chosen: ", 0, 70, 1);
        tft_g.drawString(chosen_card, 60, 70, 1);
      }
      if (button2 == 1 || strlen(discarded) == 15){ //button2 short press -> finish turn, POST discarded cards, fix to limit number of cards discarded to 5
        discarded[strlen(discarded) - 1] = '\0';
        tft_g.drawString("Discarded!: ", 0, 80, 1);
        tft_g.drawString(discarded, 70, 80, 1);
        requestPOST("discard", "NULL", discarded);
        sprintf(discarded, ""); //reset discarded string
        hand_index = 0;
      }
    }
    else {
      tft_g.drawString("Not your turn.", 0, 100, 1);
    }
  }
  if (strcmp(GAME_STATE, "BET_2") == 0){
    //Serial.println("It's betting time (again)!");
    displayCards(false);
    if (strcmp(CURRENT_PLAYER, USER_ID) == 0){
      tft_g.drawString("Add Bet: ", 0, 60, 1);
      tft_g.drawString("         ", 0, 100, 1); //clear the "not your turn" message
      if (button1 == 1){ //button1 short press -> add to bet only on screen
        bet_added = bet_added + 1;
        char tempStr[10];
        sprintf(tempStr, "%d", bet_added);
        tft_g.drawString(tempStr, 60, 60, 1);
      }
      if (button2 == 1){ //button2 short press -> finish turn, POST bet
        char tempStr[10];
        sprintf(tempStr, "%d", bet_added); 
        requestPOST("bet", tempStr, "NULL");
        bet_added = 0;
      }
    }
    else {
      tft_g.drawString("Not your turn.", 0, 100, 1);
    }
  }
  if (strcmp(GAME_STATE, "REVEAL") == 0){
    //Serial.println("It's revealing time!");
    displayCards(true);
    tft_g.drawString("Short press 1 = restart!.", 0, 100, 1);
    if (button1 == 1){ //button1 short press -> restart 
      requestPOST("restart", "NULL", "NULL");
    }
    else if (button2 == 2){ //button1 long press -> quit
      requestPOST("leave", "NULL", "NULL");
      result = 1;
    }
  }
  
  return result;
}

void Poker::makeGame() {
  char action[] = "generate";
  requestPOST(action,"NULL", "NULL"); // add yourself (user) to the game
}

void Poker::getGame(){
  requestGET();
  parser(response_buffer, "|");
}

void Poker::parser(char* data_array, char* delim){
  // Returns first token
  char *token = strtok(data_array, delim); 
  int i = 0;
  while (token != NULL) 
  { 
      //printf("%s\n", token); 
      //Serial.println(i);
      indexField(i, token);
      token = strtok(NULL, delim); 
      i++;
    }
  int_extractor(BETS, bets, ',');
} 

void Poker::indexField(int i, char* token){
  switch(i){
    case 0: 
      sprintf(CURRENT_PLAYER, token);
      //Serial.println(CURRENT_PLAYER);
    break;
    
    case 1:
    {
      sprintf(CURRENT_HAND, token);
      sprintf(card_1, "%c%c", CURRENT_HAND[0], CURRENT_HAND[1]);
      sprintf(card_2, "%c%c", CURRENT_HAND[3], CURRENT_HAND[4]);
      sprintf(card_3, "%c%c", CURRENT_HAND[6], CURRENT_HAND[7]);
      sprintf(card_4, "%c%c", CURRENT_HAND[9], CURRENT_HAND[10]);
      sprintf(card_5, "%c%c", CURRENT_HAND[12], CURRENT_HAND[13]);
      hand_array[0]= card_1; 
      hand_array[1] = card_2;
      hand_array[2]= card_3; 
      hand_array[3] = card_4;
      hand_array[4] = card_5;
//      for (int j = 0; j <= 4; j++){
//        Serial.println(hand_array[j]);
//      }
      //Serial.println(CURRENT_HAND);
    break;
    }
  
    case 2:
      sprintf(OTHER_HAND, token);
      sprintf(other_card_1, "%c%c", OTHER_HAND[0], OTHER_HAND[1]);
      sprintf(other_card_2, "%c%c", OTHER_HAND[3], OTHER_HAND[4]);
      sprintf(other_card_3, "%c%c", OTHER_HAND[6], OTHER_HAND[7]);
      sprintf(other_card_4, "%c%c", OTHER_HAND[9], OTHER_HAND[10]);
      sprintf(other_card_5, "%c%c", OTHER_HAND[12], OTHER_HAND[13]);
      other_hand_array[0]= other_card_1; 
      other_hand_array[1] = other_card_2;
      other_hand_array[2]= other_card_3; 
      other_hand_array[3] = other_card_4;
      other_hand_array[4] = other_card_5;
      //Serial.println(OTHER_HAND);
    break;
  
    case 3:
      sprintf(GAME_STATE, token);
      //Serial.println(GAME_STATE);
    break;
  
    case 4: {
      sprintf(BETS, token);
//      char temp[50];
//      strcpy(temp, BETS);
//      int_extractor(temp, bets, ',');
//      for (int j = 0; j <= 1; j++){
//        Serial.println(bets[j]);
//      }
      //Serial.println(BETS);
    break;
    }

    case 5:
      sprintf(WINNER, "%s", token);
      //Serial.println(WINNER);
    break;

  }
}

void Poker::int_extractor(char* data_array, int* output_values, char delimiter){
    char* ptr;
    char* delPointer = &delimiter;
    ptr = strtok(data_array, delPointer);
    int i = 0;
    while (ptr != NULL)
  {
    output_values[i] = atoi(ptr);
    ptr = strtok(NULL, delPointer);
    i++;
  }
}

void Poker::displayCards(uint8_t reveal) {
  tft_g.drawLine(58, 0, 58, tft_g.height(), TFT_WHITE);
  tft_g.drawString("You:", 0, 0, 1);
  tft_g.drawString("Opponent:", 65, 0, 1);
  for (int i = 0; i < 5; i++) {
    char el[50]; 
    tft_g.drawString(hand_array[i], 0, 10 + i * 10, 1);
  }
  tft_g.drawString("Bet:", 0, 140, 1);
  tft_g.drawString("Bet:", 65, 140, 1);
  char temp[4];
  sprintf(temp, "%d", bets[0]);
  tft_g.drawString(temp, 0, 150, 1);

  if (reveal == false) { //not displaying opponent's cards
      sprintf(temp, "%d", bets[1]);
      tft_g.drawString(temp, 65, 150, 1);
  } else { //show all of opponent's cards
    for (int i = 0; i < 5; i++) {
      tft_g.drawString(other_hand_array[i], 65, 10 + i * 10, 1);
      sprintf(temp, "%d", bets[1]);
      tft_g.drawString(temp, 65, 150, 1);
    }

    if (strcmp(WINNER, USER_ID) == 0){ // you are the winner!
      displayWon();
    }
    else if (strcmp(WINNER, "None") == 0){
      displayTie();
    }
    else {
      displayLost();
    }
  }
}

void Poker::displayLost() {
  tft_g.setTextColor(TFT_RED, TFT_BLACK);
  tft_g.drawString("REVEAL!", 0, 110, 2);
  char temp [50];
  sprintf(temp, "YOU LOST %d!", bets[0]);
  tft_g.drawString(temp, 0, 130, 1);
  tft_g.setTextColor(TFT_GREEN, TFT_BLACK);
}

void Poker::displayWon() {
  tft_g.setTextColor(TFT_RED, TFT_BLACK);
  int win_amt = bets[0] + bets[1];
  tft_g.drawString("REVEAL!", 0, 110, 2);
  char temp [50];
  sprintf(temp, "YOU WON %d! :)", win_amt);
  tft_g.drawString(temp, 0, 130, 1);
  tft_g.setTextColor(TFT_GREEN, TFT_BLACK);
}

void Poker::displayTie() {
  tft_g.setTextColor(TFT_RED, TFT_BLACK);
  tft_g.drawString("GAME OVER - TIE", 0, 110, 2);
  tft_g.setTextColor(TFT_GREEN, TFT_BLACK);
}

void Poker::requestPOST(char* action, char* bet_value, char* discarded_cards) {
  char body[200]; //for body;
  if (strcmp(action, "generate") == 0 || strcmp(action, "restart") == 0 || strcmp(action, "fold") == 0 || strcmp(action, "leave") == 0){ // simple POST requests only requiring user ID -> generate, restart, fold, leave
    sprintf(body, "action=%s&user=%s",action,USER_ID); //generate body, posting to User, 1 step
    int body_len = strlen(body); //calculate body length (for header reporting)
    sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/salazarj/Poker/poker.py HTTP/1.1\r\n");
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
    strcat(request_buffer, "\r\n"); //new line from header to body
    strcat(request_buffer, body); //body
    strcat(request_buffer, "\r\n"); //header
    do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
  }
 if (strcmp(action, "bet") == 0){ // POST request requiring more than user ID -> bet
    sprintf(body, "action=%s&user=%s&value=%s",action,USER_ID,bet_value); //generate body, posting to User, 1 step
    int body_len = strlen(body); //calculate body length (for header reporting)
    sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/salazarj/Poker/poker.py HTTP/1.1\r\n");
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
    strcat(request_buffer, "\r\n"); //new line from header to body
    strcat(request_buffer, body); //body
    strcat(request_buffer, "\r\n"); //header
    do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
 }
 if (strcmp(action, "discard") == 0){ // POST request requiring more than user ID -> discard
    sprintf(body, "action=%s&user=%s&cards=%s",action,USER_ID,discarded_cards); //generate body, posting to User, 1 step
    int body_len = strlen(body); //calculate body length (for header reporting)
    sprintf(request_buffer, "POST http://608dev-2.net/sandbox/sc/salazarj/Poker/poker.py HTTP/1.1\r\n");
    strcat(request_buffer, "Host: 608dev-2.net\r\n");
    strcat(request_buffer, "Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer + strlen(request_buffer), "Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
    strcat(request_buffer, "\r\n"); //new line from header to body
    strcat(request_buffer, body); //body
    strcat(request_buffer, "\r\n"); //header
    do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
 }
}

void Poker::requestGET() { // response format: CURRENT_PLAYER|CURRENT_HAND|OTHER_HAND|STATE|BETS|WINNER|
  sprintf(request_buffer, "GET /sandbox/sc/salazarj/Poker/poker.py?get=%s", USER_ID);
  strcat(request_buffer, " HTTP/1.1\r\n");
  strcat(request_buffer, "Host: iesc-s3.mit.edu\r\n");
  strcat(request_buffer, "\r\n"); //add blank line!
  do_http_request("608dev-2.net", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT, true);
}
