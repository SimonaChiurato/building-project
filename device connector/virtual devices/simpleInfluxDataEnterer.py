import paho.mqtt.client as PahoMQTT
import time
import json
from virtual_devices import simpleSubscriber as sub
from datetime import datetime
# from influxdb import InfluxDBClient
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import numpy as np


class MyInfluxDataEnterer:

	def __init__(self, location, clientID, topic, broker="localhost", port=1883, QoS=2, influx_broker="localhost",
				 influx_port=8086):
		self.location = location
		self.clientID = clientID
		self.topic = topic
		self.broker = broker
		self.port = port
		self.QoS = QoS
		self.influx_broker = influx_broker
		self.influx_port = influx_port
		self.wait = False
		self.define_MQTT()
		self.define_Influx()

	def define_MQTT(self):
		self.myMqttClient_sub = sub.MySubscriber(self.clientID, topic=self.topic, broker=self.broker, port=self.port,
												 notifier=self, QoS=self.QoS)

	def define_Influx(self):
		self.url = "https://eu-central-1-1.aws.cloud2.influxdata.com"
		self.token = '0wxFhWuucGQ61AadyidJcJr6li81JlYZybEHt-9v9XFqLZN8x1ndLiog4K3CnRDKYm8N1N2wa7rVuR91hY_Gtg=='
		self.org = 'Dev Team'
		self.write_options = SYNCHRONOUS
		self.bucket = self.location
		self.myInfluxClient = influxdb_client.InfluxDBClient(url=self.url, token=self.token, org=self.org)
		self.write_api = self.myInfluxClient.write_api(write_options=self.write_options)
		self.buckets_api = self.myInfluxClient.buckets_api()
		is_bucket_present = False
		for bucket in self.buckets_api.find_buckets().buckets:
			if bucket.name == self.location:
				is_bucket_present = True
		if is_bucket_present == False:
			self.buckets_api.create_bucket(bucket_name=self.location, org=self.org)

	def start(self):
		self.myMqttClient_sub.start()

	def stop(self):
		self.myMqttClient_sub.stop()

	def notify(self, msg):
		self.wait = True
		data = json.loads(msg.payload)
		zones = []
		for key in data['data'].keys():
			if key.split('_')[0] == 'Tin':
				zones.append(key.split('_')[1])
		for zone in zones:
			data['data'][f'PMV_{zone}'], data['data'][f'PPD_{zone}'] = self.compute_pmv_ppd(data['data'][f'Tin_{zone}'],
																							data['data'][f'MRT_{zone}'],
																							data['data'][f'Hum_{zone}'])
			data['data'][f'OpT_{zone}'] = self.compute_OpT(data['data'][f'Tin_{zone}'], data['data'][f'MRT_{zone}'])
		for key in data['data'].keys():
			_value = float(data['data'][key])
			_t = data['t']
			_block = None
			_zone = None
			_wall = None
			if key == 'T_ext':
				_id = key
				_unit = 'C'
			elif key == 'Wind_Speed':
				_id = key
				_unit = 'm/s'
			elif key == 'Wind_Direction':
				_id = key
				_unit = 'deg'
			elif key == 'DHI':
				_id = key
				_unit = 'W/m^2'
			elif key == 'DNI':
				_id = key
				_unit = 'W/m^2'
			elif key == 'Electricity':
				_id = key
				_unit = 'Wh'
			elif key == 'DistrictHeating':
				_id = key
				_unit = 'Wh'
			elif key == 'DistrictCooling':
				_id = key
				_unit = 'Wh'
			elif key.split('_')[0] == 'Tin':
				_id = key.split('_')[0]
				_unit = 'C'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'Hum':
				_id = key.split('_')[0]
				_unit = '%'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'MRT':
				_id = key.split('_')[0]
				_unit = 'C'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'CO2':
				_id = key.split('_')[0]
				_unit = 'ppm'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'PMV':
				_id = key.split('_')[0]
				_unit = 'pts'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'PPD':
				_id = key.split('_')[0]
				_unit = '%'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[0] == 'OpT':
				_id = key.split('_')[0]
				_unit = 'C'
				_block = key.split('_')[1].split(':')[0]
				_zone = key.split('_')[1].split(':')[1]
			elif key.split('_')[-2] + '_' + key.split('_')[-1] == 'winshade_status':
				_id = key.split('_')[-2] + '_' + key.split('_')[-1]
				_unit = ''
				_block = key.split('_')[0].split(':')[0]
				_zone = key.split('_')[0].split(':')[1]
				_wall = key.split('_')[1] + '_' + key.split('_')[2] + '_' + key.split('_')[3] + '_' + key.split('_')[
					4] + '_' + key.split('_')[5] + '_' + key.split('_')[6] + '_' + key.split('_')[7]
			else:
				raise Exception('Invalid measurement key')

			reformatted_time = self.cast_time(_t)
			# point = (Point(_id).tag('value', _value).field('unit', _unit).field('t', _t).field('block', _block).field('zone', _zone).field('wall', _wall))
			point = (
				Point(_id).field('value', _value).tag('unit', _unit).tag('block', _block).tag(
					'zone', _zone).tag('wall', _wall)) \
				.time(datetime(2023, 6, reformatted_time['day'], reformatted_time['hour'], reformatted_time['minute'],
							   reformatted_time['second']))

			self.write_api.write(bucket=self.bucket, org=self.org, record=point)
			time.sleep(1)  # separate points by 1 second
		self.wait = False


	def cast_time(self, date_string):
		'2023-06-08 06:15:00 con _t'
		date = date_string.split(' ')[0]
		time = date_string.split(' ')[1]
		return {
			'year': int(date.split('-')[0]),
			'month': int(date.split('-')[1]),
			'day': int(date.split('-')[2]),
			'hour': int(time.split(':')[0]),
			'minute': int(time.split(':')[1]),
			'second': int(time.split(':')[2])
		}

	def compute_OpT(self, ta, tr):
		return (ta + tr) / 2

	def compute_pmv_ppd(self, ta, tr, rh, vel=0.1, met=1.2, clo=0.7, wme=0, standard="ISO 7730-2006"):
		"""Return Predicted Mean Vote (PMV) and Predicted Percentage of
		Dissatisfied (PPD) calculated in accordance to ISO 7730-2006 standard.

		:param df: dataframe containing at least "Date/Time",
			"T_db_i[C]", "T_rad_i[C]" and "RH_i[%]" columns.
			Optional "Occupancy column" accepting only 0 and 1 values.
		:type df: class:`pandas.core.frame.DataFrame`
		:param vel: relative air speed, defaults 0.1
		:type vel: float, optional
		:param met: metabolic rate, [met] defaults 1.2
		:type met: float, optional
		:param clo: clothing insulation, [clo] defaults 0.5
		:type clo: float, optional
		:param wme: external work, [met] defaults 0
		:type wme: float, optional
		:param standard: Currentl unused, defaults to "ISO 7730-2006"
		:type standard: str, optional
		:param filter_by_occupancy: It can be set 0 or 1, depending on wether
			activate occupancy filtering on thermal comfort KPIs computation or
			not, defaults to 0.
		:type filter_by_occupancy: int, optional
		:return: DataFrame containing PMV and PPD hourly values.
		:rtype: class:`pandas.core.frame.DataFrame`
		"""

		fnps = np.exp(16.6536 - 4030.183 / (ta + 235))  # water vapor pressure in ambient air kPa
		pa = rh * 10 * fnps  # partial water vapor pressure in ambient air
		icl = 0.155 * clo  # thermal insulation of the clothing in M2K/W
		m = met * 58.15  # metabolic rate in W/M2
		w = wme * 58.15  # external work in W/M2
		mw = m - w  # internal heat production in the human body

		# ratio of clothed body surface over total body surface
		if icl <= 0.078:
			fcl = 1 + (1.29 * icl)
		else:
			fcl = 1.05 + (0.645 * icl)

		# heat transfer coefficient by forced convection
		hcf = 12.1 * np.sqrt(vel)

		# temperatures in Kelvin
		taa = ta + 273
		tra = tr + 273

		# iterative computation of clothing surface temperature
		tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1)  # first tempt

		p1 = icl * fcl
		p2 = p1 * 3.96
		p3 = p1 * 100
		p4 = p1 * taa
		p5 = (308.7 - 0.028 * mw) + (p2 * (tra / 100.0) ** 4)
		xn = tcla / 100
		xf = tcla / 50
		# end criterion
		eps = 0.00015

		n = 0  # number of iterations
		err = False
		while abs(xn - xf) > eps and err == False:
			xf = (xf + xn) / 2
			# heat transfer coefficient for natural convection
			hcn = 2.38 * abs(100.0 * xf - taa) ** 0.25
			if hcf > hcn:
				hc = hcf
			else:
				hc = hcn
			xn = (p5 + p4 * hc - p2 * xf ** 4) / (100 + p3 * hc)
			n += 1
			if n > 150:
				err = True

		if err:
			pmv = np.inf
			ppd = 100
		else:
			# clothing surface temperature
			tcl = 100 * xn - 273

			# heat loss diff. through skin
			hl1 = 3.05 * 0.001 * (5733 - (6.99 * mw) - pa)
			# heat loss by sweating
			if mw > 58.15:
				hl2 = 0.42 * (mw - 58.15)
			else:
				hl2 = 0
			# latent respiration heat loss
			hl3 = 1.7 * 0.00001 * m * (5867 - pa)
			# dry respiration heat loss
			hl4 = 0.0014 * m * (34 - ta)
			# heat loss by radiation
			hl5 = 3.96 * fcl * (xn ** 4 - (tra / 100.0) ** 4)
			# heat loss by convection
			hl6 = fcl * hc * (tcl - ta)
			# conversion coefficient of thermal sensation
			ts = 0.303 * np.exp(-0.036 * m) + 0.028

			# final formulas
			pmv = round(ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6), 1)
			ppd = int(100.0 - 95.0 * np.exp(-0.03353 * pow(pmv, 4.0) - 0.2179 * pow(pmv, 2.0)))

		return pmv, ppd


if __name__ == "__main__":
	test = MySubscriber('VirtualBuilding')
	test.start()
	while (True):
		pass
