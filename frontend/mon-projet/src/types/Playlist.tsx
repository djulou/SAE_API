export type Playlist = {
  // Champs API Backend
  playlist_id: number
  playlist_name: string
  user_id?: number
  tracks?: any[]

  // Champs UI (compatibilité avec les mocks existants)
  title?: string
  creator?: string
  pochette?: string
}