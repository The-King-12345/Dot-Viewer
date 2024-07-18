import React from 'react'

export default function Yardline() {
  const yardlines = [
    { left: 0 },
    { left: 5 },
    { left: 10 },
    { left: 15 },
    { left: 20 },
    { left: 25 },
    { left: 30 },
    { left: 35 },
    { left: 40 },
    { left: 45 },
    { left: 50 },
    { left: 55 },
    { left: 60 },
    { left: 65 },
    { left: 70 },
    { left: 75 },
    { left: 80 },
    { left: 85 },
    { left: 90 },
    { left: 95 },
    { left: 100 }
  ];

  return (
    <>
      {yardlines.map(item => (
        <div className="yardline" key={item.left} style={{ left: `${item.left}%` }}></div>
      ))}
    </>
  )
}