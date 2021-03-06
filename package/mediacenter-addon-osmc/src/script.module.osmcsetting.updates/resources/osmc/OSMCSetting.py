'''

	The settings for OSMC are handled by the OSMC Settings Addon (OSA).

	In order to more easily accomodate future changes and enhancements, each OSMC settings bundle (module) is a separate addon.
	The module can take the form of an xbmc service, an xbmc script, or an xbmc module, but it must be installed into the users'
	userdata/addons folder.

	The OSA leverages the settings interface provided by XBMC. Each addon has its own individual settings defined in a
	settings.xml file located in the addon's resources/ folder.

	The OSG detects changes to the settings by identifying the differences between a newly read settings.xml and the values from 
	a previously read settings.xml.

	The values of the settings displayed by the OSG are only ever populated by the items in the settings.xml. [Note: meaning that 
	if the settings data is retrieved from a different source, it will need to be populated in the module before it is displayed
	to the user.]

	Each module must have in its folder, a sub-folder called 'resources/osmc'. Within that folder must reside this script (OSMCSetting.py), 
	and the icons to be used in the OSG to represent the module (FX_Icon.png and FO_Icon.png for unfocused and focused images
	respectively).

	When the OSA creates the OSMC Settings GUI (OSG), these modules are identified and the OSMCSetting.py script in each of them 
	is imported. This script provides the mechanism for the OSG to apply the changes required from a change in a setting.

	The OSMCSetting.py file must have a class called OSMCSettingClass as shown below.

	The key variables in this class are:

		addonid							: The id for the addon. This must be the id declared in the addons addon.xml.

		reboot_required					: A boolean to declare if the OS needs to be rebooted. If a change in a specific setting 
									 	  requires an OS reboot to take affect, this is flag that will let the OSG know.

		setting_data_method 			: This dictionary contains:
												- the name of all settings in the module
												- the current value of those settings
												- [optional] apply - a method to call for each setting when the value changes
												- [optional] translate - a method to call to translate the data before adding it to the 
												  setting_data_method dict. The translate method must have a 'reverse' argument which 
												  when set to True, reverses the transformation.  



	The key methods of this class are:

		open_settings_window			: This is called by the OSG when the icon is clicked. This will open the settings window.
										  Usually this would be __addon__.OpenSettings(), but it could be any other script.
										  This allows the creation of action buttons in the GUI, as well as allowing developers 
										  to script and skin their own user interfaces.

		[optional] first_method			: called before any individual settings changes are applied.

		[optional] final_method			: called after all the individual settings changes are done.

		[optional] boot_method			: called when the OSA is first started.

		apply_settings					: This is called by the OSG to apply the changes to any settings that have changed.
										  It calls the first setting method, if it exists. 
										  Then it calls the method listed in setting_data_method for each setting. Then it 
										  calls the final method, again, if it exists.

		populate_setting_data_method	: This method is used to populate the setting_data_method with the current settings data.
										  Usually this will be from the addons setting data stored in settings.xml and retrieved
										  using the settings_retriever_xml method.

										  Sometimes the user is able to edit external setting files (such as the Pi's config.txt).
										  If the developer wants to use this source in place of the data stored in the
										  settings.xml, then they should edit this method to include a mechanism to retrieve and 
										  parse that external data. As the window shown in the OSG populates only with data from 
										  the settings.xml, the developer should ensure that the external data is loaded into that
										  xml before the settings window is opened.


		settings_retriever_xml			: This method is used to retrieve all the data for the settings listed in the 
										  setting_data_method from the addons settings.xml.

	The developer is free to create any methods they see fit, but the ones listed above are specifically used by the OSA.

	Settings changes are applied when the OSG is called to close. But this behaviour can be changed to occur when the addon
	settings window closes by editing the open_settings_window. The method apply_settings will still be called by OSG, so 
	keep that in mind.

'''


# XBMC Modules
import xbmcaddon
import xbmc


def log(message):
	xbmc.log(msg = 'OSMC UPDATES ' + str(message), level=xbmc.LOGDEBUG)


class OSMCSettingClass(object):

	''' 
		A OSMCSettingClass is way to substantiate the settings of an OSMC settings module, and make them available to the 
		OSMC Settings Addon (OSA).

	'''

	def __init__(self):

		''' 
			The setting_data_method contains all the settings in the settings group, as well as the methods to call when a
			setting_value has changed and the existing setting_value. 
		'''

		self.addonid = "script.module.osmcsetting.updates"
		self.me = xbmcaddon.Addon(self.addonid)

		# this is what is displayed in the main settings gui
		self.shortname = 'Updates'

		self.description = 	"""OSMC is contantly in development, with new features and up-stream bug fixes becoming available periodically.
[CR]Keep an eye out for the 'Update Available' icon on the Home screen of Kodi.
[CR]The primary purpose of this module is to allow you to set the time at which OSMC will check for updates.
If your device is on all the time, you may want to set this to be very early in the morning.
"""

		self.setting_data_method = 	{}

		# 'mercury': 	{
		# 					'setting_value' : '',
		# 					'apply'			: self.method_to_apply_changes_X,
		# 					'translate'		: self.translate_on_populate_X,
		# 					},

		# 'venus': 	{'setting_value' : ''},
		# 'earth': 	{'setting_value' : ''},
		# 'mars': 	{'setting_value' : ''},
		# 'jupiter': 	{'setting_value' : ''},
		# 'saturn': 	{'setting_value' : ''},
		# 'uranus': 	{'setting_value' : ''},
		# 'neptune': 	{'setting_value' : ''},
		# 'pluto': 	{'setting_value' : ''},									

		# }

		# populate the settings data in the setting_data_method
		self.populate_setting_data_method()

		# a flag to determine whether a setting change requires a reboot to take effect
		self.reboot_required = False

		log('START')
		for x, k in self.setting_data_method.iteritems():
			log("%s = %s" % (x, k.get('setting_value','no setting value')))


	def populate_setting_data_method(self):

		'''
			Populates the setting_value in the setting_data_method.
		'''

		# this is the method to use if you are populating the dict from the settings.xml
		latest_settings = self.settings_retriever_xml()

		# cycle through the setting_data_method dict, and populate with the settings values
		for key in self.setting_data_method.keys():

			# grab the translate method (if there is one)
			translate_method = self.setting_data_method.get(key,{}).get('translate',{})

			# get the setting value, translate it if needed
			if translate_method:
				setting_value = translate_method(latest_settings[key])
			else:
				setting_value = latest_settings[key]

			# add it to the dictionary
			self.setting_data_method[key]['setting_value'] = setting_value


	def open_settings_window(self):

		'''
			The method that determines what happens when the item is clicked in the settings GUI.
			Usually this would be __addon__.OpenSettings(), but it could be any other script.
			This allows the creation of action buttons in the GUI, as well as allowing developers to script and skin their 
			own user interfaces.
		'''

		self.me.openSettings()

		# code placed here will run when the modules settings window is closed
		# the code below ensures that the apply_settings method is called immediately after closing the settings window
		# self.apply_settings()

		log('END')
		for x, k in self.setting_data_method.iteritems():
			log("%s = %s" % (x, k.get('setting_value','no setting value')))


	def apply_settings(self):

		'''
			This method will apply all of the settings. It calls the first_method, if it exists. 
			Then it calls the method listed in setting_data_method for each setting. Then it calls the
			final_method, again, if it exists.
		'''

		# retrieve the current settings from the settings.xml (this is where the user has made changes)
		new_settings = self.settings_retriever_xml()

		# call the first method, if there is one
		try:
			self.first_method()
		except:
			pass


		# apply the individual settings changes
		for k, v in self.setting_data_method.iteritems():

			# get the application method and stored setting value from the dictionary
			method = v.get('apply', False)
			value  = v.get('setting_value', '')

			# if the new setting is different to the stored setting then change the dict and run the 'apply' method
			if new_settings[k] != value:

				# change stored setting_value to the new value
				self.setting_data_method[k]['setting_value'] = new_settings[k]

				# if a specific apply method exists for the setting, then call that
				try:
					method(setting_value)
				except:
					pass


		# call the final method if there is one
		try:
			self.final_method()
		except:
			pass



	def settings_retriever_xml(self):

		''' 
			Reads the stored settings (in settings.xml) and returns a dictionary with the setting_name: setting_value. This 
			method cannot be overwritten.
		'''

		latest_settings = {}

		addon = xbmcaddon.Addon(self.addonid)

		for key in self.setting_data_method.keys():

			latest_settings[key] = addon.getSetting(key)

		return latest_settings


	##############################################################################################################################
	#																															 #
	def first_method(self):

		''' 
			The method to call before all the other setting methods are called.

			For example, this could be a call to stop a service. The final method could then restart the service again. 
			This can be used to apply the setting changes.

		'''	

		pass


	def final_method(self):

		''' 
			The method to call after all the other setting methods have been called.

			For example, in the case of the Raspberry Pi's settings module, the final writing to the config.txt can be delayed
			until all the settings have been updated in the setting_data_method. 

		'''

		pass


	def boot_method(self):

		''' 
			The method to call when the OSA is first activated (on reboot)

		'''

		pass

	#																															 #
	##############################################################################################################################


	##############################################################################################################################
	#																															 #

	''' 
		Methods beyond this point are for specific settings. 
	'''

	# SETTING METHOD
	def method_to_apply_changes_X(self, data):

		'''
			Method for implementing changes to setting x.

		'''

		log('hells yeah!')

	def translate_on_populate_X(self, data, reverse=False):

		'''
			Method to translate the data before adding to the setting_data_method dict.

			This is useful if you are getting the populating from an external source like the Pi's config.txt.
			This method could end with a call to another method to populate the settings.xml from that same source.
		'''

		# this is how you would negate the translateing of the data when the settings window closes.
		if reverse:
			return data

	#																															 #
	##############################################################################################################################

if __name__ == "__main__":
	pass