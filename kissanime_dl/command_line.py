import kissanime_dl

def main():
	try:
		kissanime_dl.main()
	except Exception as e:
		kissanime_dl.printClr("Uh oh, an error occurred.", kissanime_dl.Color.BOLD, kissanime_dl.Color.RED)
		kissanime_dl.printClr("Go to https://github.com/wileyyugioh/kissanime_dl to report bugs.", kissanime_dl.Color.BOLD, kissanime_dl.Color.RED)
		print("Caught Error: " + repr(e) )

