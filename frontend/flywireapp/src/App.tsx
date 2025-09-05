import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useState } from 'react'

import './index.css'
import './App.css'




function App() {

  const [rootId, setRootId] = useState('')
  const [mesh, setMesh] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [neuronInfo, setNeuronInfo] = useState(null)
  

  const API_BASE_URL = 'http://localhost:8002'

  const handleSubmit = async () => {
    if (!rootId.trim()) {
      setError('Root ID is required')
      return
    }

    setLoading(true)
    setError('')

    try {

      const infoResponse = await fetch(`${API_BASE_URL}/neuron_info/${rootId}`)
      const neuronInfo  = await infoResponse.json()

      if(neuronInfo.error) {
        throw new Error(neuronInfo.error)
      }
      setNeuronInfo(neuronInfo)

    }
    catch (err) {

      setError(err instanceof Error ? err.message : 'An error occurred')
      setNeuronInfo(null)
    }
    finally {
      setLoading(false)
    } 
    }














  
  return (
    <>  
      <h1>Flywire App</h1>






    Root ID: <Input />

    <Button>Submit</Button>
    </>
  )
}

export default App
