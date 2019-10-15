
import numpy
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors
import warnings

def grayify(colors):
	RGB_weight = [0.299, 0.587, 0.114]
	luminance = (numpy.dot(colors[:, :3] ** 2, RGB_weight))**0.5
	return luminance.reshape((-1,1)) + numpy.zeros((1,3))

good_cmaps = ['Spectral', 'rainbow', 'YlOrRd', 'spectral', 'RdYlBu', 'GnBu']

def create(n, cmap='YlGnBu', avoid_white=True):
	"""
	cmap
	"""
	cm = matplotlib.cm.get_cmap(cmap)
	colors = cm(numpy.linspace(0, 1, cm.N))
	gray = grayify(colors)
	sign = numpy.sign(gray[1:] - gray[:-1])
	if not numpy.all(sign[sign != 0] == sign[sign!=0][0]):
		warnings.warn('This cmap ("%s") is not monotonic in grayscale!' % cmap)
	colors = cm(numpy.linspace(0, 1, n))
	if avoid_white:
		hsv_colors = matplotlib.colors.rgb_to_hsv(colors[:,:3])
		hsv_colors[:,2] = numpy.where(hsv_colors[:,2] > 0.9, 0.9, hsv_colors[:,2])
		#hsv_colors[:,1] = numpy.where(hsv_colors[:,1] < 0.5, 0.5, hsv_colors[:,1])
		colors = matplotlib.colors.hsv_to_rgb(hsv_colors)
	#colors = grayify(colors)
	return colors.tolist()

"""
Similar to :create:, but meant for many categories so that neighbouring colors are different
"""
def for_categories(n, cmap = 'Spectral', avoid_white=True):
	cm = matplotlib.cm.get_cmap(cmap)
	colors = cm(numpy.linspace(0, 1, n))
	colors_order = []
	for i in range(n/3):
		colors_order += [i, i+n/3, i+2*n/3]
	colors = colors[colors_order]
	
	if avoid_white:
		hsv_colors = matplotlib.colors.rgb_to_hsv(colors[:,:3])
		hsv_colors[:,2] = numpy.where(hsv_colors[:,2] > 0.9, 0.9, hsv_colors[:,2])
		colors = matplotlib.colors.hsv_to_rgb(hsv_colors)
	return colors.tolist()

