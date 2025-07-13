import { Line } from 'react-chartjs-2'

const data = {
  labels: ['1 Juil', '2 Juil', '3 Juil', '4 Juil', '5 Juil', '6 Juil', '7 Juil'],
  datasets: [
    {
      label: 'Déchets collectés (kg)',
      data: [12, 19, 14, 21, 17, 25, 20],
      fill: false,
      backgroundColor: '#2F855A',
      borderColor: '#2F855A',
      tension: 0.3
    }
  ]
}

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
  }
}

const Tendancechartbymonth = () => {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-lg h-full">
      <h2 className="text-xl font-semibold text-[#2F855A] mb-4">Tendance des déchets collectés par mois</h2>
      <Line data={data} options={options} />
    </div>
  )
}

export default Tendancechartbymonth
