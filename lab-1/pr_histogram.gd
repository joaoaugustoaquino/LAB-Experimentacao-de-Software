extends Node2D

var buckets = []

func set_data(data):

	buckets.clear()
	buckets.resize(10)

	for i in 10:
		buckets[i] = 0

	for repo in data:

		var prs = repo["prs"]

		var index = clamp(int(prs / 500), 0, 9)

		buckets[index] += 1

	queue_redraw()


func _draw():

	var x = 50
	var width = 50

	for value in buckets:

		var height = value * 2

		draw_rect(Rect2(x, 400 - height, width, height), Color.GREEN)

		x += 60
