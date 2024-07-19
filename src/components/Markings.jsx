import React from 'react'
import Hash from "./Hash"
import Sideline from "./Sideline"
import Yardline from "./Yardline"
import Number from "./Number"

export default function Markings() {
  return (
    <>
      <Hash top={100/3}/>
      <Hash top={200/3}/>
      <Yardline />
      <Sideline />
      <Number top="15.25" flipped={true}/>
      <Number top="84.75"/>
    </>
  )
}
