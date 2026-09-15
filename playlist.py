class Playlist:
    def __init__(self):
        self.songs = []

    def add_song(self, name, duration):
        self.songs.append({
            "name": name,
            "duration": duration
        })
        print(f'Песня "{name}" успешно добавлена.')

    def remove_song(self, name):
        for song in self.songs:
            if song["name"] == name:
                self.songs.remove(song)
                print(f'Песня "{name}" удалена из плейлиста.')
                return
        print(f'Ошибка: Песня "{name}" не найдена в плейлисте.')

    def total_duration(self):
        return sum(song["duration"] for song in self.songs)

    def __len__(self):
        return len(self.songs)

    def __str__(self):
        if not self.songs:
            return "Плейлист пуст."

        result = "Список песен в плейлисте:\n"
        for index, song in enumerate(self.songs, start=1):
            result += f'{index}. {song["name"]} ({song["duration"]} сек)\n'
        return result.strip()


if __name__ == "__main__":
    my_playlist = Playlist()

    print(my_playlist)
    print(f"Количество песен: {len(my_playlist)}")
    print(f"Общая продолжительность: {my_playlist.total_duration()} сек\n")

    my_playlist.add_song("Bohemian Rhapsody", 354)
    my_playlist.add_song("Song 1", 200)
    my_playlist.add_song("Song 2", 300)

    print(my_playlist)
    print(f"Количество песен: {len(my_playlist)}")
    print(f"Общая продолжительность: {my_playlist.total_duration()} сек\n")

    my_playlist.remove_song("Song 1")

    print(my_playlist)
    print(f"Количество песен: {len(my_playlist)}\n")

    my_playlist.remove_song("Shape of You")
