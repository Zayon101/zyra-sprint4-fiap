import { useState } from 'react';
import { perguntasFrequentes } from '../../data/faq';
import ItemFaq from '../ItemFaq/ItemFaq';

export default function ListaFaq() {
    const [idAberto, setIdAberto] = useState<number | null>(null);

    function alternarItem(id: number) {
        setIdAberto((atual) => (atual === id ? null : id));
    }

    return (
        <div
            className="
                mx-auto
                flex
                w-full
                max-w-[72rem]
                flex-col
                gap-[1.2rem]

                mobile-lg:gap-[1.4rem]

                tablet:gap-[1.6rem]
            "
        >
            {perguntasFrequentes.map((item) => (
                <ItemFaq
                    key={item.id}
                    item={item}
                    aberto={item.id === idAberto}
                    aoAlternar={alternarItem}
                />
            ))}
        </div>
    );
}