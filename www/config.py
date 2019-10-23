import config_default

def merge(defaults, override):
	r = {}
	for k, v in defaults.items():
		if k in override:
			if isinstance(v, dict):
				r[k] = merge(v, override[k])
			else:
				r[k] = override[k]
		else:
			r[k] = v
	return r


try:
	import config_override
	# print(config_override.configs)
	# print(config_default.configs)
	configs = merge(config_default.configs, config_override.configs)
except ImportError:
	configs = config_default.configs
	pass
# print(configs)