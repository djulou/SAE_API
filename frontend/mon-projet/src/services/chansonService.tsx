import type { Chanson } from '../types/Chanson'
import viteLogo from '/vite.svg'

export function getChansons(): Chanson[] {
  return [
    {
      title: 'Let It Go',
      artist: 'Idina Menzel',
      pochette: viteLogo,
    },
    {
      title: 'Into the Unknown',
      artist: 'Idina Menzel',
      pochette: viteLogo,
    },
  ]
}
