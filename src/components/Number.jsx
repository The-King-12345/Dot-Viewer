import React from 'react'

export default function Number(props) {
  const { top = 0 } = props;
  const { flipped = false } = props;

  let transform = "translate(-50%, -50%)";

  if (flipped == true) {
    transform = "translate(-50%, -50%) rotate(180deg)";
  }

  const numbers = [
    { value: 0, left: 0 },
    { value: 5, left: 5 },
    { value: 10, left: 10 },
    { value: 15, left: 15 },
    { value: 20, left: 20 },
    { value: 25, left: 25 },
    { value: 30, left: 30 },
    { value: 35, left: 35 },
    { value: 40, left: 40 },
    { value: 45, left: 45 },
    { value: 50, left: 50 },
    { value: 45, left: 55 },
    { value: 40, left: 60 },
    { value: 35, left: 65 },
    { value: 30, left: 70 },
    { value: 25, left: 75 },
    { value: 20, left: 80 },
    { value: 15, left: 85 },
    { value: 10, left: 90 },
    { value: 5, left: 95 },
    { value: 0, left: 100 }
  ];


  return (
    <>
      {numbers.map(item => (
        <div 
          className="number"
          key={`${item.left}-${top}`} 
          style={{ top: `${top}%`, left: `${item.left}%`, transform: transform}}
        >
          {item.value}
        </div>
      ))}
    </>
  )
}