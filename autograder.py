import json

if __name__ == '__main__':
    # Chargement des données du fichier bestScores.json
    filePath = "savedBestSolutions/bestScores.json"
    with open(filePath, "r", encoding="utf-8") as file:
        dataRaw = json.load(file)

    instancesRaw = ['eternity_A.txt', 'eternity_B.txt', 'eternity_C.txt', 'eternity_D.txt', 'eternity_E.txt',
                    'eternity_complet.txt']

    maxConnection = [40, 112, 144, 180, 220, 544]
    lower = [0, 0, 0, 0, 0, 0]
    upper = [0, 0, 0, 180, 220, 0]
    points = [1, 1, 1, 2, 2, 0]
    result = [1000 for _ in range(6)]

    total = 0
    for solver in dataRaw:
        for idx, instance in enumerate(instancesRaw):
            if instance in dataRaw[solver]:
                result[idx] = min(result[idx], dataRaw[solver][instance]["score"])

    for idx, instance in enumerate(instancesRaw):
        if upper[idx] == 0:
            pointsReçu = points[idx] if result[idx] == lower[idx] else 0
        else:
            pointsReçu = (upper[idx] - result[idx]) / (upper[idx]) * points[idx]
        print(f"{instance} : {result[idx]}/{maxConnection[idx]} - {round(pointsReçu, 2)}/{points[idx]}")

        total += pointsReçu

    print(f"Total : {round(total, 2)}/{sum(points)}")
