#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import uuid
import json
import datetime	
import logging

import paho.mqtt.client as mqtt
import fliclib

conf = configparser.ConfigParser()
conf.read(['flic2mqtt.ini','flic2mqtt_local.ini'])

""" BUTTONS = {\
	"80:e4:da:71:5a:19" : "blå" , \
	"80:e4:da:71:5f:5b" : "gul",  \
	"80:e4:da:70:1f:1b" : "hvid", \
	"80:e4:da:71:3f:66" : "grøn", \
	"80:e4:da:70:3a:66" : "sort", \
	"80:e4:da:71:4e:ac" : "sort2"} """

log = logging.getLogger(__name__)
logging.basicConfig(
    level=conf["LOG"]["LEVEL"],
    format="%(levelname)s %(module)s.%(funcName)s %(message)s",
)
log.info(f"Starting service loglevel={conf['LOG']['LEVEL']} ")

BUTTONS={}

conf_buttons=conf['FLIC']['BUTTONS'].split(',')
conf_names=conf['FLIC']['Names'].split(',')
for i in range(len(conf_buttons)):
	BUTTONS[conf_buttons[i].strip()]=conf_names[i].strip()
log.info(BUTTONS)
		
MQTT_BROKER = conf['MQTT']['Ip']

def buttonPressed(bd_addr, click_type,was_queued,time_diff):
	buttonname=BUTTONS.get(bd_addr,"noname")
	if was_queued==0:
		log.info("Flic " + buttonname +" "+ click_type)	
		mqtt_client = mqtt.Client("Flic2mqtt")
		mqtt_client.connect(MQTT_BROKER)
		msg = {'time_send':str(datetime.datetime.now()),'clicktype':click_type, 'knap':buttonname,'adresse':bd_addr,'time_diff':time_diff, 'msg_uuid':str(uuid.uuid4())}
		result = mqtt_client.publish("smarthome/flic/"+buttonname,json.dumps(msg))
		if result[0]!=0: logger.error(f"Error sending message to mqtt. {result}")
		mqtt_client.disconnect()
		
	else:
		log.error("Flic kø " + buttonname+" "+ click_type + " time_diff="+str(time_diff))

def got_info2(items):
	for bd_addr in items["bd_addr_of_verified_buttons"]:
		log.info("Flic knap fundet " +BUTTONS.get(bd_addr,"noname")+" "+ bd_addr)

def got_button(bd_addr):
	cc = fliclib.ButtonConnectionChannel(bd_addr)
	log.info("Flic knap fundet " +BUTTONS.get(bd_addr,"noname") +" "+ bd_addr)
	cc.on_button_single_or_double_click_or_hold = \
		lambda channel, click_type, was_queued, time_diff: \
			buttonPressed(channel.bd_addr,str(click_type),was_queued,time_diff)		
	cc.on_connection_status_changed = \
		lambda channel, connection_status, disconnect_reason: \
			log.debug("Flic " +bd_addr+ " "+ BUTTONS.get(bd_addr,"noname") +" "+channel.bd_addr + " " + str(connection_status) + (" " + str(disconnect_reason) if connection_status == fliclib.ConnectionStatus.Disconnected else ""))
	client.add_connection_channel(cc)

def got_info(items):
	for bd_addr in items["bd_addr_of_verified_buttons"]:
		got_button(bd_addr)
	
			
def main():
	
	client.get_info(got_info)
	client.on_new_verified_button = got_button
	client.handle_events()

client = fliclib.FlicClient("localhost")

if __name__ == "__main__":
    main()
