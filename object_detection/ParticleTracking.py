#!/usr/bin/python
import numpy as np 
import matplotlib.pyplot as plt
import time

class ParticleArray:
	def __init__(self,N):
		self.setNewState([])
		self.N = N 									# Number of Particles
		self.PartArray_curr = np.zeros((self.N,2))
		self.PartArray_next = np.zeros((self.N,2))
		self.PartArray_prev = np.zeros((self.N,2))

	#--------------------------
	# Setters and Getters
	def setNewState(self,x_new):
		self.newState = x_new
	def getNewState(self):
		return self.newState
	def setLastMovement(self):
		self.lastMovement = np.mean(self.PartArray_curr-self.PartArray_prev,axis=0)
	def getLastMovement(self):
		return self.lastMovement

	def UpdateParticles(self):
		# Update Particles
		#    Main Part of the Class: This will simulate the movement of the particles
		# 	 This takes empty events into account
		self.setLastMovement()
		partArray = np.ones((self.N,2))

		if self.newState == []:
			myMove = np.ones((self.N,2))*(np.mean(self.PartArray_curr,axis=0) - np.mean(self.PartArray_prev,axis=0))
		else:
			myMove = np.ones((self.N,2))*(self.newState - np.mean(self.PartArray_curr,axis=0))
		print("myMove")
		print(myMove)
		gaussNoise = np.random.normal(loc = 0.0, size=(self.N,2))
		self.PartArray_next = self.PartArray_curr + myMove+gaussNoise

		if self.newState != []:
			self.PartArray_prev = self.PartArray_curr
			self.PartArray_curr = self.PartArray_next 

	def PlotParticles(self):
		# This plots the particles over time
		# This also takes empty events into account
		plt.figure(1)
		#plt.ion()
		plt.subplot(2,2,1)
		if self.newState != []:
			plt.plot(self.newState[0],self.newState[1],'x')
		plt.ylabel('Position y')
		plt.xlabel('Position x')
		plt.title('Particle Array - New Data')
		
		plt.subplot(2,2,2)
		plt.plot(self.PartArray_prev[:,0],self.PartArray_prev[:,1],'s',mfc='none')
		plt.ylabel('Position y')
		plt.xlabel('Position x')
		plt.title('Particle Array - Previous')

		plt.subplot(2,2,3)
		plt.plot(self.PartArray_curr[:,0],self.PartArray_curr[:,1],'o',mfc='none')
		plt.ylabel('Position y')
		plt.xlabel('Position x')
		plt.title('Particle Array - Current')

		plt.subplot(2,2,4)
		plt.plot(self.PartArray_next[:,0],self.PartArray_next[:,1],'*')
		plt.ylabel('Position y')
		plt.xlabel('Position x')
		plt.title('Particle Array - Next')

		plt.draw()
		plt.show(block=False)
		plt.pause(1)


def exampleCode():
	# Number of Particles
	N = 50

	# Number of Steps
	steps = 4

	# Generate a randomized set of incoming data
	x_new = list(np.random.randint(low=0, high=100, size=(steps,2)))
	
	x_new[2] = []
	# Create Class Object
	T = ParticleArray(N)

	# Iterate through the data
	for k in list(range(len(x_new))):
		x = x_new[k]
		T.setNewState(x)
		T.UpdateParticles()
		print("New State:  " + str(T.newState))
		print("Particles:  ") 
		print(T.PartArray_prev,T.PartArray_curr,T.PartArray_next)
		T.PlotParticles()
		

	plt.show()
	print("End of Code.")

