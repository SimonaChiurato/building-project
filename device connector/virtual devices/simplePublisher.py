import paho.mqtt.client as PahoMQTT
import time
import pandas as pd
import json

class MyPublisher:
	def __init__(self, clientID, broker = "localhost", port = 1883):
		self.clientID = clientID
		self.broker = broker
		self.port = port

		self._paho_mqtt = PahoMQTT.Client(self.clientID, False)
		
		self._paho_mqtt.on_connect = self.myOnConnect

	def start (self):
		print(f"{self.clientID} starting")
		self._paho_mqtt.connect(self.broker, self.port)
		self._paho_mqtt.loop_start()

	def stop (self):
		print(f"{self.clientID} stopping")
		self._paho_mqtt.loop_stop()
		self._paho_mqtt.disconnect()

	def myPublish(self, topic, message, QoS = 2):
		self._paho_mqtt.publish(topic, message, QoS)

	def myOnConnect (self, paho_mqtt, userdata, flags, rc):
		print(f"{self.clientID} connected to {self.broker} with result code: {rc}")

if __name__ == "__main__":
	test = MyPublisher("MyPublisher")
	test.start()
	df=pd.read_csv('data.csv',sep=',',decimal=',',index_col=0)
	df.index=pd.to_datetime(df.index,unit='s')
	GATEWAY_NAME="VirtualBuilding"
	for i in df.index:
		for j in df.loc[i].items():
			nodeID=j[0]
			value=j[1]
			if nodeID=='Power':
				measurement="Power"
			else:
				measurement="Temperature"
			payload={
						"location":str(GATEWAY_NAME),
						"measurement":measurement,
						"node":str(nodeID),
						"time_stamp":str(i),
						"value":value}
			test.myPublish ('Action', json.dumps(payload)) 	
			time.sleep(0.1)

	test.stop()


