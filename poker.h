#ifndef Poker_h
#define Poker_h
#include "Arduino.h"
#include "Request.h"

#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display

class Poker{
  public:
    char USER_ID[50];
    TFT_eSPI tft_g;
    int initialized;
    int result;
    char request_buffer[IN_BUFFER_SIZE];
    char response_buffer[OUT_BUFFER_SIZE];
    char host[20];
    char CURRENT_PLAYER[50];
    char GAME_STATE[50]; 
    char PREV_STATE[50];
    char CURRENT_HAND[100];
    char BETS[50];
    char WINNER[50];
    char OTHER_HAND[100];
    char card_1[5];
    char card_2[5];
    char card_3[5];
    char card_4[5];
    char card_5[5];
    char other_card_1[5];
    char other_card_2[5];
    char other_card_3[5];
    char other_card_4[5];
    char other_card_5[5];
    char* hand_array[5];
    char* other_hand_array[5];
    char discarded[50];
    char chosen_card[5];
    int hand_index;
    int bets[2];
    int bet_added;
    uint32_t timer;
    Poker(char* user_id, TFT_eSPI tft);//, uint8_t pin1, uint8_t pin2);
    virtual int update(int button1,int button2);
  private:
    virtual void makeGame();
    virtual void getGame();
    virtual void parser(char* data_array, char* delim);
    virtual void indexField(int i, char* token);
    virtual void int_extractor(char* data_array, int* output_values, char delimiter);
    virtual void displayCards(uint8_t reveal);
    virtual void displayLost();
    virtual void displayWon();
    virtual void displayTie();
    virtual void requestPOST(char* action, char* bet_value, char* discarded_cards);
    virtual void requestGET();
    
};


#endif
