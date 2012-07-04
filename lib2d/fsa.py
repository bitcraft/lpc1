"""
Copyright 2010, 2011  Leif Theden


This file is part of lib2d.

lib2d is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

lib2d is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with lib2d.  If not, see <http://www.gnu.org/licenses/>.
"""

"""
modified state machine.  controls player input

output an animation if input is valid

usage:
	add states and transitions

when input is recv'd, call process with the input

check the avatar's state
determin if we can continue
return animation if ok, else return False

internal state should generally match the avatar.

lazy internal state.  ie: don't really spend too much trying to keep in sync
w/avatar.  just check it as needed.

state = (animation object, current frame)
"""

import sys

DEBUG = True

def debug(text):
	if DEBUG: sys.stdout.write(text)



STICKY = 1

ANIMATION_CHANGE_TOKEN = 0
HOLD_TOKEN = 1
UNHOLD_TOKEN = 2

from time import time as ms
from collections import deque
from pygame.locals import *



# only have one child, an avatar.
class FSA(object):
	def __init__(self, avatar):
		self.avatar = avatar	    	# avatar we are attached to
		self.combos = {}			    # input combos
		self.holds = {}			        # keep track of state changes from holds
		self.hold = 0				    # keep track of buttons held down
		self.state_transitions=deque()  # conditions for changing animations
		avatar.set_fsa(self)
		self.locked = False

		# for combos
		self.move_history = []

	def reset(self):
		self.locked = False
		self.holds = {}
		self.hold =  0
		self.move_history = []

	def lock(self):
		self.locked = True
		
	def unlock(self):
		self.locked = False

	def check_hold(self, state):
		""" avatar wants to change the animation (usually just the frame,
		we have the option of overriding it here.
		return a animation if override is to be used used for recording
		move (animation) history as well.
		no real need to update every frame...yet

		more like a request than a statement... "please, can i change state"?

		return:
			False: Not holding
			True:	 Holding, don't change the state
		"""

		anim, frame_no = state

		# DON'T CHANGE THIS!!!
		if self.hold == 0:
			return False
		else:
			for cmd, a in self.holds.items():
				if ((self.hold & cmd) == cmd) and (a == anim):			
					debug("DENY state change req. %s %s\n" % (state, self.hold))
					return True

			debug("OK state change req. %s %s\n" % (state, self.hold))
			return False

	def set_anim(self, anim):
		if anim.name == "idle":
			""" avatar wants to idle, but lets make sure player isn't holding
			down any keys first.
			"""
			self.move_history = []
		else:
			self.move_history.append(anim)

	# sticky means the avartar should finish the previous animation
	# when new one finishes
	# used for stances, (crouch to sweep, block to punch, etc)
	def add_transition(self, cmd, state1, state2, frame2=0, frame1=-1, flags=0):
		"""
		add new "transition".

		these are basically just new states with a condition
		"""

		# store the tranistions as objects, not strings
		try:
			state1 = ( self.avatar.get_animation(state1), frame1 )
			state2 = ( self.avatar.get_animation(state2), frame2 )
		except KeyError:
			raise

		# index:  0      1       2       3
		t =      (cmd, state1, state2, flags)
		self.state_transitions.append(t)

	def add_combo(self, animation, *combo):
		"""
		add a new combo.

		a combo is a list of animations.  if it matches the command history,
		then execute another animation.
		"""

		# bug: we should raise if a duplicate combo is attempted to be added

		# create a temp ref for speed
		getter = self.avatar.get_animation

		# make a list of animation objects for the list of names
		cooked = tuple([ getter(a) for a in combo ])

		# store it in our lookup hash thingy
		self.combos[cooked] = (getter(animation), 0)

	def set_default_transition(self, t):
		pass

	def get_transition(self, cmd, state):
		if self.locked:
			return False

		# return a state if possible
		#print "===================================================="
		for t in self.state_transitions:
			t_frame = t[1][1]
			if (t[0] & cmd == cmd) and (t[1][0] == state[0]):
				if (t_frame == state[1]) or (t_frame == -1):
					return t
		return False

	def process(self, cmd, pressed):
		state = self.avatar.state
		if pressed:
			self.hold += cmd
			state = self.check_change(cmd, state)

			# this key caused a state change.  let's remember that
			if state != False:
				self.holds[cmd] = state[0]

			return state

		else:
			# sanity, i guess
			if self.hold & cmd == cmd:
				old_hold = self.hold
				self.hold -= cmd

				debug("KEYUP %s %s %s\n" % (cmd, self.hold, old_hold))

				# sometimes fails, not sure why
				try:
					del self.holds[cmd]
				except KeyError:
					pass

				# still holding a key
				if self.hold != 0:
					t = self.get_transition(self.hold, state)
					if t != False:
						debug("hold: %s\n" % self.hold)
						if t[3] & STICKY == STICKY:
							return t[2]

		return False

	# see if this event will change our state, return animation if true
	def check_change(self, cmd, state):
		t = self.get_transition(cmd, state)
		if not t:
			# the input isn't valid
			return False

		else:
			# input is valid, check if it makes a combo
			return self.get_combo(t[2])

	def get_combo(self, state):
		# return a combo if it exists, otherwise return the original state

		# we need a temp tuple to check if a combo has been entered
		# don't set move_history b/c the avatar will do it (self.set_state)
		temp = self.move_history[:]
		temp.append(state[0])

		#print "history: ", temp

		# check for a combo
		try:
			new_state = self.combos[tuple(temp)]
			self.move_history = []
			return new_state

		except KeyError:
			return state

	def update(self, time):
		pass


