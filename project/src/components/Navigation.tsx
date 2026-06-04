import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface NavigationProps {
  sections: string[];
}

export function Navigation({ sections }: NavigationProps) {
  const [activeSection, setActiveSection] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsVisible(window.scrollY > 200);

      const scrollPosition = window.scrollY + 100;
      const sectionElements = sections.map(id => document.getElementById(id));

      for (let i = sectionElements.length - 1; i >= 0; i--) {
        const element = sectionElements[i];
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(i);
          break;
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [sections]);

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{
        y: isVisible ? 0 : -100,
        opacity: isVisible ? 1 : 0
      }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-navy-100 shadow-sm"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <span className="text-sm font-semibold text-navy-900 tracking-tight">
            Clustering Study Viewer
          </span>
          <div className="flex items-center gap-6">
            {sections.map((section, index) => (
              <a
                key={section}
                href={`#${section}`}
                className={`text-xs font-medium transition-colors duration-200 ${
                  activeSection === index
                    ? 'text-navy-900'
                    : 'text-navy-500 hover:text-navy-700'
                }`}
              >
                {section.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
              </a>
            ))}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
