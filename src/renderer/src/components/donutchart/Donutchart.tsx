import React, { useEffect, useRef } from 'react'
import Chart from 'chart.js/auto'
import { FaRecycle } from 'react-icons/fa'


const DonutChart: React.FC = () => {
  const chartRef = useRef<HTMLCanvasElement | null>(null)
  const totalDechets = 120 + 90 + 150

  useEffect(() => {
    const ctx = chartRef.current?.getContext('2d')
    if (!ctx) return

    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Plastique', 'Papier', 'Organique'],
        datasets: [
          {
            data: [120, 90, 150],
            backgroundColor: ['#2F855A', '#9FAD72', '#C4E1B9'], 
            borderColor: '#ffffff',
            borderWidth: 3,
            hoverOffset: 15,
            hoverBorderColor: '#2F855A'
          }
        ]
      },
      options: {
        cutout: '70%',
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 10,
            backgroundColor: '#2F855A',
            titleColor: '#fff',
            bodyColor: '#E6F0DA',
            cornerRadius: 6,
            callbacks: {
              label: (ctx) => {
                const data = ctx.dataset.data as number[]
                const total = data.reduce((a, b) => a + b, 0)
                const val = ctx.raw as number
                const percent = ((val / total) * 100).toFixed(1)
                return `${ctx.label}: ${val} déchets (${percent}%)`
              }
            }
          }
        },
        maintainAspectRatio: false,
        responsive: true
      }
    })

    return () => {
      chart.destroy()
    }
  }, [])

  return (
    <div className="bg-white rounded-3xl shadow-lg p-6 ">
      <h2 className="text-2xl font-semibold text-[#2F855A] mb-6 text-center flex items-center justify-center gap-2">
              <FaRecycle />
              Total des déchets 
      </h2>

      <div className="relative w-full h-56 mx-auto flex">
        <canvas ref={chartRef}></canvas>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none z-0">
          <span className="text-3xl font-bold text-[#2F855A]">{totalDechets}</span>
          <span className="text-sm text-gray-500 mt-1">Total déchets</span>
        </div>
      </div>

      <div className="mt-8 flex justify-around font-medium text-sm select-none">
        <div className="flex items-center gap-2 text-[#2F855A]">
          <span className="block w-4 h-4 rounded-full bg-[#2F855A]"></span> Organique:{' '}
          <span className="font-semibold ml-1">150</span>
        </div>
        <div className="flex items-center gap-2 text-[#9FAD72]">
          <span className="block w-4 h-4 rounded-full bg-[#9FAD72]"></span> Papier:{' '}
          <span className="font-semibold ml-1">90</span>
        </div>
        <div className="flex items-center gap-2 text-[#C4E1B9]">
          <span className="block w-4 h-4 rounded-full bg-[#C4E1B9] border border-[#2F855A]"></span>{' '}
          Plastique: <span className="font-semibold ml-1">120</span>
        </div>
      </div>
    </div>
  )
}

export default DonutChart
