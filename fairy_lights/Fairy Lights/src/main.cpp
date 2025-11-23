#include <FastLED.h>
#include <stdint.h>

// Taken from https://github.com/FastLED/PlatformIO-Starter

#define LED_PIN         10
#define NUM_LEDS        1
#define BRIGHTNESS      128
#define LED_TYPE        WS2812
#define COLOR_ORDER     RGB
CRGB leds[NUM_LEDS];

void setup() {
    FastLED.addLeds<LED_TYPE, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
    FastLED.setBrightness(BRIGHTNESS);
}

void setColor(int color) {
    leds[0] = color;
    FastLED.show();
    delay(1000);
    leds[0] = CRGB::Black;
    FastLED.show();
    delay(1000);
}

void loop() {
    setColor(CRGB::Red);
    setColor(CRGB::Orange);
    setColor(CRGB::Green);
    setColor(CRGB::Blue);
    setColor(CRGB::Purple);
    // setColor(CRGB::Violet);
    // setColor(CRGB::Black);
}
