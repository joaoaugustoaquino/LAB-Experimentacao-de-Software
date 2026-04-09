extends Node2D

var counts = {}
var font : FontFile

func _ready():
	font = load("res://fonts/Roboto-Regular.ttf")

func set_data(data):

	var temp = {}

	for repo in data:

		var lang = repo["language"]

		if !temp.has(lang):
			temp[lang] = 0

		temp[lang] += 1

	var sorted = temp.keys()

	sorted.sort_custom(func(a,b): return temp[a] > temp[b])

	counts.clear()

	for i in min(10, sorted.size()):

		var lang = sorted[i]
		counts[lang] = temp[lang]


func _draw():

	var x = 50
	var width = 40

	for lang in counts:

		var value = counts[lang]

		var height = value * 2

		draw_rect(Rect2(x, 400 - height, width, height), Color.BLUE)

		draw_string(font, Vector2(x, 420), lang)

		x += 60
