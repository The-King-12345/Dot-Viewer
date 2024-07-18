import Hash from "./components/Hash"
import Sideline from "./components/Sideline"
import Yardline from "./components/Yardline"
import Number from "./components/Number"
import Dot from "./components/Dot"
import './App.css'

function App() {
  return (
    <main>
      <Hash top={100/3}/>
      <Hash top={200/3}/>
      <Yardline />
      <Sideline />
      <Number top="15.25" flipped={true}/>
      <Number top="84.75"/>

      <Dot top="50" left="50"/>
    </main>
  )
}

export default App
