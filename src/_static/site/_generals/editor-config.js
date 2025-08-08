// editor-config.js
const initEditor = () => {
    const editor = grapesjs.init({
        container: '#gjs',
        height: '100vh',
        width: 'auto',
        storageManager: {
            type: 'remote',
            stepsBeforeSave: 1,
            urlStore: '{% url "moderation:save_landing" %}',
            urlLoad: '{% url "moderation:load_landing" %}',
            params: {
                slug: '{{ object.slug|default:"" }}',
            },
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        },

        // Панели инструментов
        panels: {
            defaults: [
                {
                    id: 'layers',
                    el: '.panel__right',
                    resizable: {
                        maxDim: 350,
                        minDim: 200,
                        tc: 0,
                        cl: 1,
                        cr: 0,
                        bc: 0,
                        keyWidth: 'flex-basis',
                    },
                },
                {
                    id: 'panel-switcher',
                    el: '.panel__switcher',
                    buttons: [
                        {
                            id: 'show-layers',
                            active: true,
                            label: 'Layers',
                            command: 'show-layers',
                            togglable: false,
                        },
                        {
                            id: 'show-style',
                            active: true,
                            label: 'Styles',
                            command: 'show-styles',
                            togglable: false,
                        },
                        {
                            id: 'show-traits',
                            active: true,
                            label: 'Traits',
                            command: 'show-traits',
                            togglable: false,
                        }
                    ],
                }
            ]
        },

        // Менеджер стилей
        styleManager: {
            sectors: [{
                name: 'General',
                open: false,
                buildProps: ['float', 'display', 'position', 'top', 'right', 'left', 'bottom']
            },{
                name: 'Dimension',
                open: false,
                buildProps: ['width', 'height', 'max-width', 'min-height', 'margin', 'padding'],
            },{
                name: 'Typography',
                open: false,
                buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-align', 'text-decoration', 'text-shadow'],
            },{
                name: 'Decorations',
                open: false,
                buildProps: ['border-radius-c', 'background-color', 'border-radius', 'border', 'box-shadow', 'background'],
            }],
        },

        // Менеджер блоков
        blockManager: {
            appendTo: '#blocks',
            blocks: [
                {
                    id: 'section',
                    label: '<b>Section</b>',
                    attributes: { class:'gjs-block-section' },
                    content: `
                        <section class="py-16 px-4">
                            <div class="container mx-auto">
                            </div>
                        </section>
                    `,
                },
                {
                    id: 'text',
                    label: 'Text',
                    content: '<div data-gjs-type="text">Insert your text here</div>',
                },
                {
                    id: 'image',
                    label: 'Image',
                    select: true,
                    content: { type: 'image' },
                    activate: true
                }
            ]
        },

        // Настройка устройств для адаптивного дизайна
        deviceManager: {
            devices: [{
                name: 'Desktop',
                width: '', // full width
            }, {
                name: 'Tablet',
                width: '768px',
                widthMedia: '768px',
            }, {
                name: 'Mobile',
                width: '320px',
                widthMedia: '320px',
            }]
        },

        // Плагины
        plugins: [
            'gjs-preset-webpage',
            'gjs-blocks-basic',
            'grapesjs-plugin-forms',
            'grapesjs-component-countdown',
            'grapesjs-plugin-export',
            'grapesjs-tabs',
            'grapesjs-custom-code',
            'grapesjs-touch',
            'grapesjs-parser-postcss',
            'grapesjs-tooltip',
            'grapesjs-tui-image-editor',
            'grapesjs-typed',
            'grapesjs-style-bg',
            editor => customBlocks.init(editor)
        ],

        // Настройки плагинов
        pluginsOpts: {
            'gjs-blocks-basic': {},
            'gjs-preset-webpage': {
                modalImportTitle: 'Import Template',
                modalImportLabel: '<div style="margin-bottom: 10px; font-size: 13px;">Paste here your HTML/CSS and click Import</div>',
                modalImportContent: function(editor) {
                    return editor.getHtml() + '<style>'+editor.getCss()+'</style>'
                },
                filestackOpts: null,
                aviaryOpts: false,
                blocksBasicOpts: {
                    flexGrid: true,
                    stylePrefix: 'gjs-',
                },
            },
            'grapesjs-tui-image-editor': {
                config: {
                    includeUI: {
                        initMenu: 'filter',
                    },
                },
                icons: {
                    'menu.normalIcon.path': '../icon-d.svg',
                    'menu.activeIcon.path': '../icon-b.svg',
                    'menu.disabledIcon.path': '../icon-a.svg',
                    'menu.hoverIcon.path': '../icon-c.svg',
                },
            },
        },

        // Настройки canvas
        canvas: {
            styles: [
                'https://cdn.tailwindcss.com',
                'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
            ],
            scripts: [
                'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js'
            ],
        },

        // Настройки редактора кода
        codeManager: {
            inlineCss: true,
        },
    });

    // Добавляем команды
    editor.Commands.add('show-layers', {
        getRowEl(editor) { return editor.getContainer().closest('.editor-row'); },
        getLayersEl(row) { return row.querySelector('.layers-container') },

        run(editor, sender) {
            const lmEl = this.getLayersEl(this.getRowEl(editor));
            lmEl.style.display = '';
        },
        stop(editor, sender) {
            const lmEl = this.getLayersEl(this.getRowEl(editor));
            lmEl.style.display = 'none';
        },
    });

    editor.Commands.add('show-styles', {
        getRowEl(editor) { return editor.getContainer().closest('.editor-row'); },
        getStyleEl(row) { return row.querySelector('.styles-container') },

        run(editor, sender) {
            const smEl = this.getStyleEl(this.getRowEl(editor));
            smEl.style.display = '';
        },
        stop(editor, sender) {
            const smEl = this.getStyleEl(this.getRowEl(editor));
            smEl.style.display = 'none';
        },
    });

    // Обработчики событий
    editor.on('component:selected', () => {
        const selectedComponent = editor.getSelected();
        if (selectedComponent) {
            console.log('Selected component:', selectedComponent.getName());
        }
    });

    editor.on('storage:store', (e) => {
        console.log('Content saved');
    });

    editor.on('storage:error', (e) => {
        console.error('Save error:', e);
    });

    return editor;
};