import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import './Profile.css';
import { ProfileHeader } from './ProfileHeader';
import { Footer } from './Footer';
import uploadIcon from '../assets/Upload.svg';
import deleteIcon from '../assets/Delete.svg';
import arrowDownIcon from '../assets/ArrowDown.svg';
import filterIcon from '../assets/Filter.svg';
import searchIcon from '../assets/Search.svg';
import rightArrow from '../assets/right-arrow.png';
import leftArrow from '../assets/left-arrow.png';
import { fileService } from '../services/files';
import type { FileResponse } from '../types';
import { useSeo } from '../hooks/useSeo';
import { getApiErrorDetail } from '../utils/getApiErrorDetail';

type FilterType = 'date' | 'size' | 'sort' | null;
type DateFilterOption = 'all' | 'today' | 'week' | 'month';
type SizeFilterOption = 'all' | 'small' | 'medium' | 'large';
type SortOption = 'date_desc' | 'date_asc' | 'name_asc' | 'name_desc' | 'size_desc' | 'size_asc';

interface ActiveFilters {
  date: DateFilterOption;
  size: SizeFilterOption;
  sort: SortOption;
}

export const Profile: React.FC = () => {
  useSeo({
    title: 'Мои файлы - Blur',
    description: 'Закрытая страница управления обработанными файлами.',
    canonicalPath: '/profile',
    noindex: true,
  });

  const [autoDelete] = useState('1 час');
  const [allFiles, setAllFiles] = useState<FileResponse[]>([]);
  const [totalFiles, setTotalFiles] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [downloadingFileId, setDownloadingFileId] = useState<number | null>(null);
  const [deletingFileId, setDeletingFileId] = useState<number | null>(null);
  
  // Активные фильтры
  const [activeFilters, setActiveFilters] = useState<ActiveFilters>({
    date: 'all',
    size: 'all',
    sort: 'date_desc'
  });
  
  // Состояние меню фильтра
  const [isFilterMenuOpen, setIsFilterMenuOpen] = useState(false);
  const [selectedFilterType, setSelectedFilterType] = useState<FilterType>(null);
  const [isSubMenuOpen, setIsSubMenuOpen] = useState(false);
  
  // Поиск по названию
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  
  // Пагинация
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(5);
  
  // URL params для сохранения состояния
  const [searchParams, setSearchParams] = useSearchParams();

  // Загрузка параметров из URL при монтировании
  useEffect(() => {
    const page = searchParams.get('page');
    const perPage = searchParams.get('perPage');
    const date = searchParams.get('date') as DateFilterOption;
    const size = searchParams.get('size') as SizeFilterOption;
    const sort = searchParams.get('sort') as SortOption;
    const search = searchParams.get('search');

    if (page) setCurrentPage(parseInt(page));
    if (perPage) setItemsPerPage(parseInt(perPage));
    
    setActiveFilters({
      date: (date && ['all', 'today', 'week', 'month'].includes(date)) ? date : 'all',
      size: (size && ['all', 'small', 'medium', 'large'].includes(size)) ? size : 'all',
      sort: (sort && ['date_desc', 'date_asc', 'name_asc', 'name_desc', 'size_desc', 'size_asc'].includes(sort)) ? sort : 'date_desc'
    });
    
    if (search) setSearchQuery(search);
  }, []);

  // Обновление URL при изменении параметров
  useEffect(() => {
    const params: Record<string, string> = {
      page: currentPage.toString(),
      perPage: itemsPerPage.toString(),
      date: activeFilters.date,
      size: activeFilters.size,
      sort: activeFilters.sort
    };
    
    if (searchQuery) {
      params.search = searchQuery;
    }
    
    setSearchParams(params);
  }, [currentPage, itemsPerPage, activeFilters, searchQuery]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearchQuery(searchQuery.trim());
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    loadFiles();
  }, [currentPage, itemsPerPage, activeFilters, debouncedSearchQuery]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fileService.getFilesPaginated({
        search: debouncedSearchQuery || undefined,
        date_filter: activeFilters.date !== 'all' ? activeFilters.date : undefined,
        size_filter: activeFilters.size !== 'all' ? activeFilters.size : undefined,
        sort: activeFilters.sort,
        page: currentPage,
        per_page: itemsPerPage,
      });
      setAllFiles(response.items);
      setTotalFiles(response.total);
      setTotalPages(response.total_pages || 1);
    } catch (err: unknown) {
      setError(getApiErrorDetail(err) || 'Ошибка при загрузке файлов');
    } finally {
      setLoading(false);
    }
  };

  const paginatedFiles = allFiles;

  // Обработчики фильтров
  const handleFilterButtonClick = () => {
    setIsFilterMenuOpen(!isFilterMenuOpen);
    setSelectedFilterType(null);
    setIsSubMenuOpen(false);
  };

  const handleFilterTypeSelect = (type: FilterType) => {
    setSelectedFilterType(type);
    setIsSubMenuOpen(true);
  };

  const handleDateFilterSelect = (value: DateFilterOption) => {
    setActiveFilters(prev => ({ ...prev, date: value }));
    setIsFilterMenuOpen(false);
    setSelectedFilterType(null);
    setIsSubMenuOpen(false);
    setCurrentPage(1);
  };

  const handleSizeFilterSelect = (value: SizeFilterOption) => {
    setActiveFilters(prev => ({ ...prev, size: value }));
    setIsFilterMenuOpen(false);
    setSelectedFilterType(null);
    setIsSubMenuOpen(false);
    setCurrentPage(1);
  };

  const handleSortSelect = (value: SortOption) => {
    setActiveFilters(prev => ({ ...prev, sort: value }));
    setIsFilterMenuOpen(false);
    setSelectedFilterType(null);
    setIsSubMenuOpen(false);
    setCurrentPage(1);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const getActiveFiltersText = (): string => {
    const parts = [];
    
    if (activeFilters.date !== 'all') {
      switch (activeFilters.date) {
        case 'today': parts.push('Сегодня'); break;
        case 'week': parts.push('Неделя'); break;
        case 'month': parts.push('Месяц'); break;
      }
    }
    
    if (activeFilters.size !== 'all') {
      switch (activeFilters.size) {
        case 'small': parts.push('Маленькие'); break;
        case 'medium': parts.push('Средние'); break;
        case 'large': parts.push('Большие'); break;
      }
    }
    
    switch (activeFilters.sort) {
      case 'date_desc': parts.push('Сначала новые'); break;
      case 'date_asc': parts.push('Сначала старые'); break;
      case 'name_asc': parts.push('По имени А-Я'); break;
      case 'name_desc': parts.push('По имени Я-А'); break;
      case 'size_desc': parts.push('По размеру ↓'); break;
      case 'size_asc': parts.push('По размеру ↑'); break;
    }
    
    return parts.join(' • ') || 'Все файлы';
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleDelete = async (fileId: number) => {
    if (!window.confirm('Удалить файл?')) return;
    try {
      setDeletingFileId(fileId);
      await fileService.deleteFile(fileId);
      await loadFiles();
    } catch {
      setError('Ошибка при удалении');
    } finally {
      setDeletingFileId(null);
    }
  };

  const handleDownload = async (file: FileResponse) => {
    try {
      setDownloadingFileId(file.id);
      await fileService.downloadFile(file.id, `processed_${file.original_filename}`);
    } catch {
      setError('Ошибка при скачивании');
    } finally {
      setDownloadingFileId(null);
    }
  };

  return (
    <>
      <ProfileHeader />
      <div className="profile-page">
        <div className="profile-storage">
          <h2 className="profile-storage-title">Мои файлы</h2>
          
          <div className="profile-content">
            <div className="profile-files">
              
              {/* Строка поиска */}
              <div className="profile-search">
                <input
                  type="text"
                  className="search-input"
                  placeholder="Поиск по названию файла..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
                <img src={searchIcon} alt="Search" className="search-icon" />
              </div>
              
              {/* Кнопка фильтра и информация */}
              <div className="profile-filter-bar">
                <div className="filter-button-container">
                  <button 
                    className="filter-main-button"
                    onClick={handleFilterButtonClick}
                  >
                    <img src={filterIcon} alt="Filter" className="filter-icon" />
                    <span>Фильтр</span>
                    <img src={arrowDownIcon} alt="▼" className="filter-arrow-icon" />
                  </button>
                  
                  {/* Иерархическое меню фильтра */}
                  {isFilterMenuOpen && (
                    <div className="filter-hierarchy-menu">
                      {!isSubMenuOpen ? (
                        /* Главное меню - типы фильтров */
                        <div className="filter-types-menu">
                          <button
                            className="filter-type-item"
                            onClick={() => handleFilterTypeSelect('date')}
                          >
                            <span>По дате</span>
                            <span className="filter-type-arrow">›</span>
                          </button>
                          <button
                            className="filter-type-item"
                            onClick={() => handleFilterTypeSelect('size')}
                          >
                            <span>По размеру</span>
                            <span className="filter-type-arrow">›</span>
                          </button>
                          <button
                            className="filter-type-item"
                            onClick={() => handleFilterTypeSelect('sort')}
                          >
                            <span>Сортировка</span>
                            <span className="filter-type-arrow">›</span>
                          </button>
                        </div>
                      ) : (
                        /* Подменю - значения фильтра */
                        <div className="filter-values-menu">
                          <button
                            className="filter-back-button"
                            onClick={() => {
                              setSelectedFilterType(null);
                              setIsSubMenuOpen(false);
                            }}
                          >
                            <span className="filter-back-arrow">‹</span>
                            <span>Назад</span>
                          </button>
                          
                          {selectedFilterType === 'date' && (
                            <>
                              <button
                                className={`filter-value-item ${activeFilters.date === 'all' ? 'active' : ''}`}
                                onClick={() => handleDateFilterSelect('all')}
                              >
                                Все файлы
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.date === 'today' ? 'active' : ''}`}
                                onClick={() => handleDateFilterSelect('today')}
                              >
                                За сегодня
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.date === 'week' ? 'active' : ''}`}
                                onClick={() => handleDateFilterSelect('week')}
                              >
                                За неделю
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.date === 'month' ? 'active' : ''}`}
                                onClick={() => handleDateFilterSelect('month')}
                              >
                                За месяц
                              </button>
                            </>
                          )}
                          
                          {selectedFilterType === 'size' && (
                            <>
                              <button
                                className={`filter-value-item ${activeFilters.size === 'all' ? 'active' : ''}`}
                                onClick={() => handleSizeFilterSelect('all')}
                              >
                                Любой размер
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.size === 'small' ? 'active' : ''}`}
                                onClick={() => handleSizeFilterSelect('small')}
                              >
                                Маленькие (&lt;100 KB)
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.size === 'medium' ? 'active' : ''}`}
                                onClick={() => handleSizeFilterSelect('medium')}
                              >
                                Средние (100 KB - 1 MB)
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.size === 'large' ? 'active' : ''}`}
                                onClick={() => handleSizeFilterSelect('large')}
                              >
                                Большие (&gt;1 MB)
                              </button>
                            </>
                          )}
                          
                          {selectedFilterType === 'sort' && (
                            <div className="filter-values-menu with-scroll">
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'date_desc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('date_desc')}
                              >
                                Сначала новые
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'date_asc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('date_asc')}
                              >
                                Сначала старые
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'name_asc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('name_asc')}
                              >
                                По имени (А-Я)
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'name_desc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('name_desc')}
                              >
                                По имени (Я-А)
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'size_desc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('size_desc')}
                              >
                                По размеру (сначала большие)
                              </button>
                              <button
                                className={`filter-value-item ${activeFilters.sort === 'size_asc' ? 'active' : ''}`}
                                onClick={() => handleSortSelect('size_asc')}
                              >
                                По размеру (сначала маленькие)
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
                
                <span className="active-filters-info">
                  {getActiveFiltersText()}
                </span>
                
                <span className="filter-count">
                  Найдено: {totalFiles}
                </span>
              </div>

              {/* Список файлов */}
              <div className="profile-files-list">
                {error && <div className="profile-error">{error}</div>}
                
                {loading ? (
                  <div className="profile-loading">Загрузка...</div>
                ) : paginatedFiles.length === 0 ? (
                  <div className="profile-empty">
                    {searchQuery || activeFilters.date !== 'all' || activeFilters.size !== 'all'
                      ? 'Нет файлов по заданным критериям' 
                      : 'Нет обработанных файлов'}
                  </div>
                ) : (
                  paginatedFiles.map((file) => (
                    <div key={file.id} className="profile-file-item">
                      <span className="file-name">{file.original_filename}</span>
                      <span className="file-date">
                        {new Date(file.created_at).toLocaleDateString()}
                      </span>
                      <span className="file-size">
                        {formatFileSize(file.file_size)}
                      </span>
                      <div className="file-actions">
                        <button 
                          className="file-action-btn upload-btn"
                          onClick={() => handleDownload(file)}
                          disabled={downloadingFileId === file.id}
                          title="Скачать"
                        >
                          <img src={uploadIcon} alt="Download" />
                        </button>
                        <button 
                          className="file-action-btn delete-btn"
                          onClick={() => handleDelete(file.id)}
                          disabled={deletingFileId === file.id}
                          title="Удалить"
                        >
                          <img src={deleteIcon} alt="Delete" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Пагинация */}
              {totalFiles > 0 && (
                <div className="profile-pagination">
                  <button
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                    disabled={currentPage === 1}
                  >
                    <img src={leftArrow} alt="Previous" style={{ width: '16px', height: '16px' }} />
                  </button>
                  
                  <span>{currentPage} / {totalPages}</span>
                  
                  <button
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <img src={rightArrow} alt="Previous" style={{ width: '16px', height: '16px' }} /> 
                  </button>
                  
                  <select 
                    value={itemsPerPage} 
                    onChange={(e) => {
                      setItemsPerPage(Number(e.target.value));
                      setCurrentPage(1);
                    }}
                  >
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                  </select>
                </div>
              )}
            </div>
            
            {/* Автоудаление */}
            <div className="profile-storage-time">
              <span className="auto-delete-text">Авто удаление через</span>
              <div className="auto-delete-select">
                <span className="auto-delete-value">{autoDelete}</span>
                <img src={arrowDownIcon} alt="▼" className="arrow-icon" />
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
};