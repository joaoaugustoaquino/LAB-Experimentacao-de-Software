extends Node2D

var buckets = []

func set_data(data):

	buckets.clear()
	buckets.resize(10)

	for i in 10:
		buckets[i] = 0

	for repo in data:

		var ratio = repo["issue_ratio"]

		var index = int(ratio * 10)

		index = clamp(index, 0, 9)

		buckets[index] += 1

	queue_redraw()
