import sys, os
import GameLogic

from Control_Poster import ors_genpos_poster

try:
   scriptRoot = os.path.join(os.environ['ORS_ROOT'],'scripts')
except KeyError:
   scriptRoot = '.'

try:
   libRoot = os.path.join(os.environ['ORS_ROOT'],'lib')
except KeyError:
   libRoot = '.'

if scriptRoot not in sys.path:
	sys.path.append(scriptRoot)
if scriptRoot not in sys.path:
	sys.path.append(libRoot)

from middleware.independent.IndependentBlender import *
import setup.ObjectData


def init(contr):
	# Middleware initialization
	if not hasattr(GameLogic, 'orsConnector'):
		GameLogic.orsConnector = MiddlewareConnector()

	# Get the object data
	ob, parent, port_name = setup.ObjectData.get_object_data(contr)

	# Get the dictionary for the robot's state
	robot_state_dict = GameLogic.robotDict[parent]

	ob['Init_OK'] = False

	try:
		# Get the dictionary for the component's state
		state_dict = GameLogic.componentDict[ob]
		ob['Init_OK'] = True
	except AttributeError:
		print ("Component Dictionary not found!")
		print ("This component must be part of a scene")
		

	if ob['Init_OK']:
		print ('######## CONTROL INITIALIZATION ########')
		
		#speed_port_name = port_name + '/vxvyvz'
		#rotation_port_name = port_name + '/rxryrz'
		#GameLogic.orsConnector.registerBufferedPortBottle([speed_port_name])
		#GameLogic.orsConnector.registerBufferedPortBottle([rotation_port_name])

		#robot_state_dict[port_name] = ors_genpos_poster.locate_poster("CLIENT_GENPOS_POSTER")
		robot_state_dict[port_name] = ors_genpos_poster.locate_poster("p3dSpeedRef")
		#robot_state_dict[port_name] = ors_genpos_poster.locate_poster("BLENDER_GENPOS_POSTER")
		print ("Poster ID found: {0}".format(robot_state_dict[port_name]))
		if robot_state_dict[port_name] == None:
			print ("ERROR creating poster. This module may not work")
			#ob['Init_OK'] = False


		print ('######## CONTROL INITIALIZED ########')
	
	
def move(contr):
	# Get the object data
	ob, parent, port_name = setup.ObjectData.get_object_data(contr)

	# Get the dictionary for the robot's state
	robot_state_dict = GameLogic.robotDict[parent]

	if ob['Init_OK']:	

	############################### SPEED #################################

		genpos_speed = ors_genpos_poster.read_genPos_data(robot_state_dict[port_name])
		#print ("Tuple type ({0}) returned".format(type(genpos_speed)))
		#print ("Tuple data: ({0}, {1})".format(genpos_speed.v, genpos_speed.w))

		vx = genpos_speed.v
		rz = genpos_speed.w

		msg_act = contr.actuators['Send_update_msg']
		#msg_act.propName = parent.name
		#msg_act.to = parent.name

		# Tick rate is the real measure of time in Blender.
		# By default it is set to 60, regardles of the FPS
		# If logic tick rate is 60, then: 1 second = 60 ticks
		ticks = GameLogic.getLogicTicRate()
		#fps = GameLogic.getAverageFrameRate()		
		#fps = fps * 2.5

		msg_act.subject = 'Speed'
		try:
			robot_state_dict['vx'] = vx / ticks
			robot_state_dict['rz'] = rz	/ ticks
		# For the moment ignoring the division by zero
		# It happens apparently when the simulation starts
		except ZeroDivisionError:
			pass

		contr.activate(msg_act)

		#print ("Motion for robot '{0}'".format(parent.name))
		#print ("\tvx: {0}\trz: {1}".format(vx, rz))
