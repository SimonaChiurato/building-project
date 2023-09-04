from . import simpleSubscriber as sub

class MyActuator():

	def __init__(self, clientID, topic, broker = "localhost", port = 1883, QoS = 2):
		self.clientID = clientID
		self.topic = topic
		self.broker = broker
		self.port = port
		self.QoS = QoS
		self.set_Globals()
		self.define_MQTT()

	def set_Globals(self):
		self.wait = True
		
	def define_MQTT(self):
		self.myMqttClient_sub = sub.MySubscriber(self.clientID, topic = self.topic, broker = self.broker, port = self.port, notifier = self, QoS = self.QoS)

	def start(self):
		self.myMqttClient_sub.start()

	def stop(self):
		self.myMqttClient_sub.stop()

	def notify(self, msg):
		self.msg = msg
		self.wait = False




