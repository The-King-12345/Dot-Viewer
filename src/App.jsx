import { useEffect, useState } from "react"
import Markings from "./components/Markings"
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
      <Markings></Markings>

      {filteredData.map((performer) => (
        <Dot key={performer.id} top={performer.Front_hash + performer.Front_steps*25/21} left={performer.Side_yd + performer.Side_steps*5/8}/>
      ))}
      
    </main>
    
  )
}

export default App
