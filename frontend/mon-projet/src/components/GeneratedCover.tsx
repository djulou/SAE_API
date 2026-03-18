import { useMemo } from "react"

type GeneratedCoverProps = {
  title: string
}


function stringHash(str: string): number {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash)
  }
  return hash
}

function generateGradient(hash: number) {
  const hue1 = Math.abs(hash) % 360
  const hue2 = (hue1 + 60) % 360
  const hue3 = (hue1 + 120) % 360

  return {
    color1: `hsl(${hue1}, 70%, 55%)`,
    color2: `hsl(${hue2}, 65%, 45%)`,
    color3: `hsl(${hue3}, 75%, 50%)`,
  }
}

function getInitials(title: string): string {
  const words = title.trim().split(" ").filter(Boolean)

  if (words.length === 0) return "?"

  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }

  return (
    words[0].charAt(0) +
    words[1].charAt(0)
  ).toUpperCase()
}


export default function GeneratedCover({ title }: GeneratedCoverProps) {
  const { gradient, initials, shapeSeed } = useMemo(() => {
    const hashValue = stringHash(title)
    const gradient = generateGradient(hashValue)
    const initials = getInitials(title)
    const shapeSeed = Math.abs(hashValue) % 100

    return { hash: hashValue, gradient, initials, shapeSeed }
  }, [title])

  return (
    <div
      className="generated-cover"
      style={{
        width: "100%",
        height: "100%",
        borderRadius: "16px",
        position: "relative",
        overflow: "hidden",
        background: `linear-gradient(135deg, ${gradient.color1}, ${gradient.color2})`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "Inter, sans-serif",
        userSelect: "none",
      }}
    >
      {/* Cercle décoratif */}
      <div
      className="cercle"
        style={{
          position: "absolute",
          width: "70%",
          height: "70%",
          borderRadius: "50%",
          background: gradient.color3,
          opacity: 0.15,
          top: `-${shapeSeed / 2}%`,
          left: `-${shapeSeed / 3}%`,
          filter: "blur(20px)",
        }}
      />

      {/* Carré décoratif */}
      <div
      className="carre"
        style={{
          position: "absolute",
          width: "40%",
          height: "40%",
          background: "rgba(0,0,0,0.1)",
          transform: `rotate(${shapeSeed}deg)`,
          bottom: `-${shapeSeed / 3}%`,
          right: `-${shapeSeed / 4}%`,
          borderRadius: "12px",
        }}
      />

      {/* Initiales */}
      <span
      className="cercle"
        style={{
          position: "relative",
          fontSize: "3rem",
          fontWeight: 700,
          color: "white",
          letterSpacing: "2px",
          textShadow: "0 4px 12px rgba(0,0,0,0.3)",
        }}
      >
        {initials}
      </span>
    </div>
  )
}