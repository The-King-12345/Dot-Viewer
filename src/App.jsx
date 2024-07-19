import { useEffect, useState } from "react"
import Hash from "./components/Hash"
import Sideline from "./components/Sideline"
import Yardline from "./components/Yardline"
import Number from "./components/Number"
import Dot from "./components/Dot"
import useFetch from "./hooks/useFetch"
import './App.css'


function App() {
  const [data, setData] = useState([]);
  const { fetchCsvData } = useFetch();

  useEffect(() => {
    fetchCsvData("/src/assets/dotsheet.csv", setData);
  }, [])

  const filteredData = data.filter(row => row.Set === 0);

  return (
    <main>
      <Hash top={100/3}/>
      <Hash top={200/3}/>
      <Yardline />
      <Sideline />
      <Number top="15.25" flipped={true}/>
      <Number top="84.75"/>

      {filteredData.map((performer) => (
        <Dot key={performer.id} top={performer.Front_hash + performer.Front_steps*25/21} left={performer.Side_yd + performer.Side_steps*5/8}/>
      ))}
      
    </main>
    
  )
}

export default App
