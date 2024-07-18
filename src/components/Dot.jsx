import React from 'react'

export default function Dot(props) {
  const { left } = props;
  const { top } = props;
  
  return (
    <div className="dot" style={{ top: `${top}%`, left: `${left}%` }}></div>
  )
}
