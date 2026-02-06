import { ReactNode, useRef } from "react"
// import "./carousel.css"

type CarouselProps = {
  children: ReactNode
}

export default function Carousel({ children }: CarouselProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  const scrollLeft = () => {
    containerRef.current?.scrollBy({ left: -300, behavior: "smooth" })
  }

  const scrollRight = () => {
    containerRef.current?.scrollBy({ left: 300, behavior: "smooth" })
  }

  return (
    <div className="carousel-wrapper">
      <button className="carousel-btn left" onClick={scrollLeft}>
        ‹
      </button>

      <div className="carousel-container" ref={containerRef}>
        {children}
      </div>

      <button className="carousel-btn right" onClick={scrollRight}>
        ›
      </button>
    </div>
  )
}

