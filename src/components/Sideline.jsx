import React from 'react'

export default function Sideline() {
  const sidelines = [
    { percentage: 0 },
    { percentage: 100 },
  ];

  return (
    <>
      {sidelines.map(item => (
        <div className="sideline" key={item.percentage} style={{ top: `${item.percentage}%` }}></div>
      ))}
    </>
  )
}
