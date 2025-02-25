from machine import Pin
import time
import dht
from umqtt.simple import MQTTClient
import network

WIFI_SSID = "AndroidAP"
WIFI_PASSWORD = "mama1234"

MQTT_BROKER = "industrial.api.ubidots.com"
MQTT_USER = "BBUS-i6IzvXyGQ3MKqoHoLawmVB9p8g5eSQ"
MQTT_PASSWORD = ""
MQTT_TOPIC = "/v1.6/devices/esp32-maverick"

dht_sensor = dht.DHT11(Pin(4))
trig_pin = Pin(14, Pin.OUT)
echo_pin = Pin(27, Pin.IN)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Menghubungkan ke Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print("Wi-Fi terhubung:", wlan.ifconfig())

def read_ultrasonic():
    trig_pin.value(0)
    time.sleep_us(2)
    trig_pin.value(1)
    time.sleep_us(10)
    trig_pin.value(0)
    
    while echo_pin.value() == 0:
        pulse_start = time.ticks_us()
    while echo_pin.value() == 1:
        pulse_end = time.ticks_us()
    
    pulse_duration = pulse_end - pulse_start
    distance = (pulse_duration * 0.0343) / 2
    return distance

def read_dht():
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        return temp, hum
    except Exception as e:
        print("Gagal membaca DHT11:", e)
        return None, None

def connect_mqtt():
    try:
        client = MQTTClient("esp32", MQTT_BROKER, user=MQTT_USER, password=MQTT_PASSWORD)
        client.connect()
        print("Terhubung ke broker MQTT")
        return client
    except Exception as e:
        print("Gagal terhubung ke MQTT:", e)
        return None

def publish_data(client, temp, hum, distance):
    try:
        payload = '{"temperature": %s, "humidity": %s, "distance": %s}' % (temp, hum, distance)
        client.publish(MQTT_TOPIC, payload)
        print("Data terkirim:", payload)
    except Exception as e:
        print("Gagal mengirim data:", e)

def main():
    connect_wifi()
    client = connect_mqtt()
    if not client:
        return
    
    while True:
        distance = read_ultrasonic()
        temp, hum = read_dht()
        if temp is not None and hum is not None:
            publish_data(client, temp, hum, distance)
        time.sleep(10)

if __name__ == "__main__":
    main()
