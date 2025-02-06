import React from 'react'
import { useState } from 'react'
import Link from 'next/link'
import Image from 'next/image'

export default function Navbar() {
  const [currentRoute, setRoute] = useState('Forschung')
  function navbarPosition(route: any) {
    setRoute(route)
  }

  return (
    <>
      <div className="flex justify-between mt-3 mb-5">
        <Link href="https://www.uni-muenster.de/de/">
          <Image
            src={require('../../public/images/wwu.svg')}
            alt="wwu"
            width={300}
            height={300}
          />
        </Link>
        <Link href="https://www.wi.uni-muenster.de/de/willkommen">
          <Image
            src={require('../../public/images/secondary_ercis_right.jpeg')}
            alt="ercis"
            width={300}
            height={300}
          />
        </Link>
      </div>
      <div className="flex flex-col">
        <div className="flex gap-4 pb-4 overflow-auto text-xl border-b-4 border-black navbar">
          <a
            href="https://www.wi.uni-muenster.de/de/studierende"
            onClick={() => navbarPosition('Studierende')}
          >
            <div
              className={
                'navbar-element ' +
                (currentRoute === 'Studierende' ? 'font-bold' : '')
              }
            >
              STUDENT AFFAIRS
            </div>
          </a>
          <div className="separator">|</div>
          <a
            href="https://www.wi.uni-muenster.de/de/studieninteressierte"
            onClick={() => navbarPosition('Studieninteressierte')}
          >
            <div
              className={
                'navbar-element flex flex-row gap-x-1.5 ' +
                (currentRoute === 'Studieninteressierte' ? 'font-bold' : '')
              }
            >
              <p>PROSPECTIVE</p> <p>STUDENTS</p>
            </div>
          </a>
          <div className="separator">|</div>
          <a href="/" onClick={() => navbarPosition('Forschung')}>
            <div
              className={
                'navbar-element ' +
                (currentRoute === 'Forschung' ? 'font-bold' : '')
              }
            >
              RESEARCH
            </div>
          </a>
          <div className="separator">|</div>
          <a
            href="https://www.wi.uni-muenster.de/de/institut"
            onClick={() => navbarPosition('Das Institut')}
          >
            <div
              className={
                'navbar-element flex flex-row gap-x-1.5 ' +
                (currentRoute === 'Das Institut' ? 'font-bold' : '')
              }
            >
              <p>THE</p>
              <p>DEPARTMENT</p>
            </div>
          </a>
          <div className="separator">|</div>
          <a
            href="https://www.wi.uni-muenster.de/de/campus"
            onClick={() => navbarPosition('Der Campus')}
          >
            <div
              className={
                'navbar-element ' +
                (currentRoute === 'Der Campus' ? 'font-bold' : '')
              }
            >
            
              CAMPUS
            </div>
          </a>
          <div className="separator">|</div>
          <a
            href="https://www.wi.uni-muenster.de/de/karriere"
            onClick={() => navbarPosition('Karriere')}
          >
            <div
              className={
                'navbar-element ' +
                (currentRoute === 'Karriere' ? 'font-bold' : '')
              }
            >
              CAREER
            </div>
          </a>
        </div>
        <div className="flex flex-row gap-2 mt-3 text-sm text-white sub-navigation">
          <Link
            href="https://www.wiwi.uni-muenster.de/"
            className="p-1 bg-[#485c8c] rounded"
          >
            SCHOOL OF BUSINESS AND ECONOMICS
          </Link>
          <Link
            href="https://www.wi.uni-muenster.de/de"
            className="p-1 bg-[#485c8c] rounded"
          >
            IS DEPARTMENT
          </Link>
          <Link
            href="https://www.ercis.org/"
            className="p-1 bg-[#485c8c] rounded"
          >
            ERCIS
          </Link>
        </div>
      </div>
    </>
  )
}
